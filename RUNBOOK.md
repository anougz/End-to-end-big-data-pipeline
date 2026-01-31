# Runbook (Execution Order)

Follow these steps in order to start the pipeline:
## 1. Infrastructure Setup

Ensure HDFS and the database are running:
start-dfs.sh

# Check if folders exist
hdfs dfs -mkdir -p /spark-logs /user/adm-mcsc/checkpoints

## 2. Messaging System

Start Zookeeper and Kafka:

zookeeper-server-start.sh -daemon /usr/local/kafka/config/zookeeper.properties
kafka-server-start.sh -daemon /usr/local/kafka/config/server.properties

## 3. Data Ingestion
Activate the virtual environment and start the producer:

source venv/bin/activate
python3 producer/earthquake_producer.py

## 4. Spark Processing
Submit the streaming job:

spark-submit --master local[*] \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  --jars ~/earthquake-pipeline/postgresql-42.7.2.jar \
  spark/spark_processor.py

## 5. Visualization (Grafana)

Access the dashboard via SSH Tunnel (if remote):

ssh -L 3000:localhost:3000 user@your-server-ip

Open your browser at http://localhost:3000.