from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import DecimalType
from schema import input_schema

SPARK_MASTER = "local[*]"
SPARK_KAFKA_JAR_DEP = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"

KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
KAFKA_TOPIC_NAME = "financial-transaction"

# create spark session
spark = (
    SparkSession.builder.appName("Streaming from Kafka")
    .config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", SPARK_KAFKA_JAR_DEP)
    .config("spark.sql.shuffle.partitions", 4)
    .master(SPARK_MASTER)
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

# read from kafka
streaming_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER)
    .option("subscribe", KAFKA_TOPIC_NAME)
    .load()
)

# process json object as per input_schema
json_df = (
    streaming_df.selectExpr("cast(value as string) as value")
    .withColumn("value", from_json(col("value"), input_schema))
    .select("value.*")
)

# parse input dataframe
parsed_json_df = (
    json_df.select([col(x).alias(x.replace(" ", "")) for x in json_df.columns])
    .withColumn("Timestamp", to_timestamp(col("Timestamp"), "yyyy/MM/dd HH:mm"))
    .withColumn("IsLaundering", col("IsLaundering").cast("boolean"))
    .withColumn("FromBank", col("FromBank").cast("int"))
    .withColumn("ToBank", col("ToBank").cast("int"))
    .withColumn("AmountReceived", col("AmountReceived").cast(DecimalType(15, 2)))
    .withColumn("AmountPaid", col("AmountPaid").cast(DecimalType(15, 2)))
)

# ingest data
query = parsed_json_df.writeStream.outputMode("Append").format("console").start()

query.awaitTermination()
