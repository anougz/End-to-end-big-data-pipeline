from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, from_unixtime, array, window, avg, max, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

# 1. Initialisation
spark = SparkSession.builder \
    .appName("EarthquakeFullPipeline") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Schéma
schema = StructType([
    StructField("id", StringType(), True),
    StructField("magnitude", DoubleType(), True),
    StructField("place", StringType(), True),
    StructField("time", LongType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("ingestion_timestamp", StringType(), True)
])

# 3. Lecture Kafka
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "10.0.0.121:9092") \
    .option("subscribe", "earthquake-events") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Transformation de base (Silver layer)
json_df = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", from_unixtime(col("time") / 1000).cast("timestamp")) \
    .withColumn("coordinates", array("longitude", "latitude"))

# 5. Étape 6 : Analytics (Agrégations par fenêtre de 5 min)
analytics_df = json_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(window(col("timestamp"), "5 minutes", "1 minute")) \
    .agg(
        count("id").alias("nb_seismes"),
        avg("magnitude").alias("mag_moyenne"),
        max("magnitude").alias("mag_max")
    ).select("window.start", "window.end", "nb_seismes", "mag_moyenne", "mag_max")

def write_to_postgres(df, batch_id):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/earthquake_db") \
        .option("dbtable", "earthquake_stats") \
        .option("user", "postgres") \
        .option("password", "admin") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

# 6. Écritures Simultanées (Sinks)

# Sink A : Archivage HDFS (Étape 5 - Raw)
query_raw = json_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/user/adm-mcsc/earthquake-pipeline/raw") \
    .option("checkpointLocation", "/user/adm-mcsc/checkpoints/raw_data") \
    .start()

# Sink B : Analytics Console (Étape 6 - Real-time stats)
query_stats = analytics_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query_db = analytics_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("complete") \
    .option("checkpointLocation", "/user/adm-mcsc/checkpoints/postgres_stats") \
    .start()

# Attendre que les flux se terminent
spark.streams.awaitAnyTermination()
