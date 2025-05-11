import os
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.avro.functions import from_avro

# Load config from environment variables
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
SCHEMA_REGISTRY_URL = f"http://{os.environ.get('SCHEMA_REGISTRY_HOST', 'schema-registry')}:{os.environ.get('SCHEMA_REGISTRY_PORT', '8081')}"
S3_BUCKET = os.environ.get("MINIO_BUCKET", "datalake")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin123")

# Database and topics
DATABASE = os.environ.get("POSTGRES_DB", "mydatabase")
SCHEMA = "public"
TABLES = ["customers", "products", "orders"]
TOPICS = [f"{DATABASE}.{SCHEMA}.{table}" for table in TABLES]

# Initialize Spark
spark = SparkSession.builder \
    .appName("KafkaAvroToDelta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT) \
    .config("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Fetch schemas from Schema Registry
schemas = {}
for topic in TOPICS:
    subject = f"{topic}-value"
    url = f"{SCHEMA_REGISTRY_URL}/subjects/{subject}/versions/latest"
    resp = requests.get(url)
    if resp.status_code == 200:
        schemas[topic] = resp.json()['schema']
        print(f"✅ Fetched schema for {topic}")
    else:
        print(f"⚠️ Warning: Schema not found for {topic} (status {resp.status_code})")

# Read from Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", ",".join(TOPICS)) \
    .option("startingOffsets", "earliest") \
    .load()

df_with_topic = df_raw.withColumn("topic_str", col("topic").cast("string"))

# Process each topic
streams = []

for topic in TOPICS:
    schema = schemas.get(topic)
    if schema:
        df_filtered = df_with_topic.filter(col("topic_str") == topic)
        df_parsed = df_filtered.withColumn("data", from_avro(col("value"), schema, {"mode": "PERMISSIVE"})) \
                               .filter(col("data").isNotNull())
        df_flat = df_parsed.selectExpr("data.*")

        query = df_flat.writeStream \
            .format("delta") \
            .option("checkpointLocation", f"s3a://{S3_BUCKET}/checkpoints/{topic}") \
            .option("path", f"s3a://{S3_BUCKET}/output/{topic}") \
            .outputMode("append") \
            .start()

        print(f"✅ Started streaming query for {topic}")
        streams.append(query)
    else:
        print(f"⏭️ Skipping {topic}: no schema found.")

# Await termination
for query in streams:
    query.awaitTermination()
