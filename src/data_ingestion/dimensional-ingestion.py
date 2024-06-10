import great_expectations as gx
from great_expectations.exceptions.exceptions import DataContextError
from pipeline import parse_aml_raw_stream
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, when, window

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

DATASOURCE_NAME = f"SparkStreaming_{KAFKA_TOPIC_NAME}"
DATA_ASSET_NAME = "dimensional_df"
MIN_COUNT_EXPECTED = 1

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

window_df_non_empty = window_df.select(
    [
        when(
            col(c) == "",
            None,
        )
        .otherwise(col(c))
        .alias(c)
        for c in window_df.columns
    ],
)


def foreach_batch_function(df, batch_id):
    write_properties = {
        "driver": DB_DRIVER,
        "user": DB_USER,
        "password": DB_PASS,
    }
    if not df.isEmpty():
        batch = df.withColumn("batch_id", lit(batch_id)).withColumn(
            "soundness",
            lit(1),
        )
        batch = _validate_batch(batch)
        batch.write.jdbc(
            url=DB_URL,
            table=f"{SCHEMA}.{TABLE}",
            mode="append",
            properties=write_properties,
        )


def _validate_batch(batch):
    context = gx.get_context()
    try:
        datasource = context.sources.add_spark(name=DATASOURCE_NAME)
    except DataContextError:
        datasource = context.datasources[DATASOURCE_NAME]
    try:
        data_asset = datasource.add_dataframe_asset(name=DATA_ASSET_NAME)
    except ValueError:
        data_asset = datasource.get_asset(DATA_ASSET_NAME)
    my_batch_request = data_asset.build_batch_request(dataframe=batch)
    validator = context.get_validator(batch_request=my_batch_request)
    for col_to_val in batch.columns:
        validator.expect_column_values_to_not_be_null(col_to_val)
    validator.expect_column_min_to_be_between("count", MIN_COUNT_EXPECTED)
    result = validator.validate()
    for res in result.get("results", []):
        if not res["success"]:
            if (
                res["expectation_config"]["expectation_type"]
                == "expect_column_values_to_not_be_null"
            ):
                batch = _handle_unexpected_nulls(batch, res)
            elif (
                res["expectation_config"]["expectation_type"]
                == "expect_column_min_to_be_between"
            ):
                batch = _handle_unexpected_min(batch)
    return batch


def _handle_unexpected_min(batch):
    return batch.withColumn("soundness", lit(0))


def _handle_unexpected_nulls(batch, res):
    unexpected_col = res["expectation_config"]["kwargs"]["column"]
    unexpected_values = res["result"]["partial_unexpected_list"]
    return batch.withColumn(
        "soundness",
        when(
            col(unexpected_col) in unexpected_values,
            0,
        ).otherwise(col("soundness")),
    )


out_query = (
    window_df_non_empty.writeStream.outputMode("append")
    .foreachBatch(foreach_batch_function)
    .start()
)
out_query.awaitTermination()
