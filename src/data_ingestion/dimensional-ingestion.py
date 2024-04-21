from pipeline import parse_aml_raw_stream
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, window

SPARK_APP_NAME = "DimensionalIngestion"
SPARK_MASTER = "local[*]"
SPARK_KAFKA_JAR_DEP = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
SPARK_POSTGRES_JAR_DEP = "org.postgresql:postgresql:42.7.3"

KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
KAFKA_TOPIC_NAME = "financial-transaction"

WATERMARK_DELAY_THRESHOLD = "1 hour"
WINDOW_DURATION = "1 hour"

DB_DRIVER = "org.postgresql.Driver"
DB_SERVER = "localhost"
DB_NAME = "postgres"
DB_URL = f"jdbc:postgresql://{DB_SERVER}/{DB_NAME}"
DB_USER = "postgres"
DB_PASS = "postgres"  # noqa: S105
SCHEMA = "public"
TABLE = "fact_transaction"

spark = (
    SparkSession.builder.appName(SPARK_APP_NAME)
    .config("spark.streaming.stopGracefullyOnShutdown", True)
    .config("spark.jars.packages", f"{SPARK_KAFKA_JAR_DEP},{SPARK_POSTGRES_JAR_DEP}")
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
window_df = (
    parsed_json_df.withWatermark("Timestamp", WATERMARK_DELAY_THRESHOLD)
    .groupBy(
        window(
            "Timestamp",
            WINDOW_DURATION,
            None,
            None,
        ),
        "From_Bank",
        "From_Account",
        "To_Bank",
        "To_Account",
    )
    .count()
    .withColumn("Window_Start", col("window.start"))
    .withColumn("Window_End", col("window.end"))
    .drop("window")
    .select(
        "window_start",
        "window_end",
        "from_bank",
        "from_account",
        "to_bank",
        "to_account",
        "count",
    )
)


def foreach_batch_function(df, batch_id):
    properties = {
        "driver": DB_DRIVER,
        "user": DB_USER,
        "password": DB_PASS,
    }
    df.withColumn("batch_id", lit(batch_id)).write.jdbc(
        url=DB_URL,
        table=f"{SCHEMA}.{TABLE}",
        mode="append",
        properties=properties,
    )


out_query = (
    window_df.writeStream.outputMode("append")
    .foreachBatch(foreach_batch_function)
    .start()
)
out_query.awaitTermination()
