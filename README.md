<<<<<<< HEAD
# End-to-end-big-data-pipeline
=======
End-to-end pipeline project

🏗 Architecture

The data flows through the following components:

    Source : https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

    Producer: Python script fetching data from USGS API and sending it to Kafka.

    Streaming: Apache Spark consumes Kafka messages, performs windowed aggregations, and computes magnitudes.

    Storage: Processed data is stored in PostgreSQL (for real-time access) and HDFS (for cold storage/archiving).

    Visualization: Grafana dashboard connected to PostgreSQL for real-time monitoring.

🛠 Prerequisites

    Hadoop Stack: HDFS 3.x, Spark 3.5.x

    Messaging: Apache Kafka 3.x

    Database: PostgreSQL 14+

    Visuals: Grafana
>>>>>>> 510c047 (Add project structure and pipeline code)
