from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringDeserializer

# Table list
TABLES = ["customers", "products", "orders"]

# Topic list (adjust 'mydatabase' to your actual database.server.name)
TOPICS = [f"mydatabase.public.{table}" for table in TABLES]

# Schema Registry config
schema_registry_conf = {
    'url': 'http://localhost:8081'  # or 'schema-registry:8081' if running inside Docker
}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Avro deserializer
value_deserializer = AvroDeserializer(schema_registry_client)

# Consumer config
consumer_conf = {
    'bootstrap.servers': 'localhost:29092',  # or 'kafka:9092' if inside Docker
    'key.deserializer': AvroDeserializer(schema_registry_client),
    'value.deserializer': value_deserializer,
    'group.id': 'avro-consumer-group',
    'auto.offset.reset': 'earliest'
}

consumer = DeserializingConsumer(consumer_conf)
consumer.subscribe(TOPICS)

print(f"Subscribed to topics: {TOPICS}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        print(f"\n--- Message from topic: {msg.topic()} ---")
        print(f"Key: {msg.key()}")
        print("Value:")
        print(msg.value())  # Avro-decoded dict

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
