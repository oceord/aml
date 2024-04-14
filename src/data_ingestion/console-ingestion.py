from pipeline import parse_aml_raw_stream
from pyspark.sql import SparkSession

SPARK_APP_NAME = "ConsoleJsonIngestion"
SPARK_MASTER = "local[*]"
SPARK_KAFKA_JAR_DEP = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"

KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
KAFKA_TOPIC_NAME = "financial-transaction"

spark = (
    SparkSession.builder.appName(SPARK_APP_NAME)
    .config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", SPARK_KAFKA_JAR_DEP)
    .config("spark.sql.shuffle.partitions", 4)
    .master(SPARK_MASTER)
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

streaming_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER)
    .option("subscribe", KAFKA_TOPIC_NAME)
    .load()
)
parsed_json_df = parse_aml_raw_stream(streaming_df)

out_query = parsed_json_df.writeStream.outputMode("append").format("console").start()
out_query.awaitTermination()
