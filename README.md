# MiniDataPlatform

A simple data engineering platform for streaming PostgreSQL data through Kafka, transforming it with Spark, and storing results in a Delta Lake format on MinIO. Built for educational purposes using Docker.

## 📦 Project Structure

- `docker-compose.yml` – Main orchestration file for services.
- `.env` – Configuration of credentials and ports (kept in version control for transparency).
- `connect/` – Kafka Connect container with Debezium + Avro converters installed.
- `init-connector/` – Registers the Debezium PostgreSQL source connector at startup.
- `spark-app/` – PySpark app that consumes Kafka Avro topics and writes Delta files to MinIO.
- `insert_data.py` – Script to insert test data into PostgreSQL.
- `consumer.py` – Optional Kafka consumer for local testing.
- `postgresql.conf` – Custom PostgreSQL config.
- `requirements.txt` – Python requirements for local tooling.

## 🚀 How It Works

1. **PostgreSQL** – Stores relational data in tables like `customers`, `products`, and `orders`.
2. **Debezium + Kafka Connect** – Captures changes (CDC) from PostgreSQL and streams them into Kafka topics.
3. **Schema Registry** – Stores Avro schemas used by Kafka topics.
4. **Spark Structured Streaming** – Reads Kafka topics, decodes Avro data, and writes results in Delta format.
5. **MinIO** – S3-compatible object store where Delta tables are stored.

> ⚠️ Changes in the PostgreSQL database are automatically captured by **Debezium**, which is installed as a plugin in the Kafka Connect container.

## 🧪 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/MiniDataPlatform.git
cd MiniDataPlatform
```

### 2. Start the Entire Stack

```bash
docker-compose up -d --build
```

> Ensure Docker and Docker Compose are installed and running.

### 3. Verify Services

- MinIO Console: http://localhost:9001  
- Schema Registry: http://localhost:8081  
- Kafka Connect (REST, should return connector name): http://localhost:8083/connectors  
- PostgreSQL: localhost:5432

### 4. Insert Sample Data

Before inserting data into the PostgreSQL database, it's recommended to set up a Python virtual environment and install required dependencies.

```bash
python -m venv venv
source venv/bin/activate        # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

Once the environment is ready, run the following script to populate the database with sample data:

```bash
python insert_data.py
```

> **Note:** This step is **required only after a fresh start** (e.g., after `docker-compose down -v`).  
> The `insert_data.py` script must be executed to make the `spark-app` run correctly,  
> as it initializes the source database with example entries used in the Spark processing job.

### 5. View Results

- Check Delta Lake output in MinIO under: `datalake/output/mydatabase.public.orders/`
- Data is partitioned by Kafka topic, with streaming checkpoints stored per topic.

### 6. Consuming Change Events with `consumer.py`

The `consumer.py` script is a Kafka consumer that listens to change data capture (CDC) events published by **Debezium** to Kafka topics corresponding to the PostgreSQL tables: `customers`, `products`, and `orders`.

```bash
python -m venv venv
source venv/bin/activate        # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

```bash
python consumer.py
```

## 7. Retriving data from datalake

After the Spark streaming job writes Delta-formatted data to MinIO, you can inspect the stored output using a standalone Python script.

The provided script ***example_retrival.py*** connects to MinIO (using boto3), lists Parquet files under the output directory, and loads the latest non-empty file from a chosen topic (e.g., orders) into a Pandas DataFrame for local analysis.

```bash
python -m venv venv
source venv/bin/activate        # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

```bash
python consumer.py
```

example output:
```
   id  customer_id  product_id  quantity            ingestion_ts
0   1            4           3         2 2025-05-11 20:09:09.080
1   2            1           5         2 2025-05-11 20:09:09.080
2   3            1           1         1 2025-05-11 20:09:09.080
3   4            5           5         4 2025-05-11 20:09:09.080
4   5            1           1         4 2025-05-11 20:09:09.080
```

## 🧾 Environment Variables

Main variables are stored in `.env`:

```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
POSTGRES_PORT=5432

MINIO_USER=minioadmin
MINIO_PASS=minioadmin123
MINIO_BUCKET=datalake

SCHEMA_REGISTRY_HOST=schema-registry
SCHEMA_REGISTRY_PORT=8081
KAFKA_BROKER=kafka:9092

S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
```

## 📂 Data Flow

```text
PostgreSQL ──> Kafka Connect + Debezium ──> Kafka ──> Spark Streaming ──> Delta Lake (MinIO)
           (CDC Events)            (Avro)       (Structured Streaming)       (S3-like)
```

## Data Transformation

After deserializing each Kafka message from Avro format, the application extracts the after.* field from Debezium-style CDC events to retrieve the latest state of the record (i.e., the post-change values).

It then adds a new column:

```python
ingestion_ts = current_timestamp()
```

This column captures the exact processing time of each record in Europe/Warsaw timezone, allowing for:

Time-based filtering and partitioning

Traceability of when data was ingested into the data lake

Better observability for real-time pipelines

## ✅ Features

- ✔️ PostgreSQL CDC streaming via Debezium
- ✔️ Kafka Avro serialization
- ✔️ Schema Registry integration
- ✔️ MinIO-compatible Delta Lake sink
- ✔️ Modular Docker-based deployment