from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import DecimalType
from schema import input_schema


def parse_aml_raw_stream(df):
    json_df = (
        df.selectExpr("cast(value as string) as value")
        .withColumn("value", from_json(col("value"), input_schema))
        .select("value.*")
    )
    return (
        json_df.select([col(x).alias(x.replace(" ", "")) for x in json_df.columns])
        .withColumn("Timestamp", to_timestamp(col("Timestamp"), "yyyy/MM/dd HH:mm"))
        .withColumn("IsLaundering", col("IsLaundering").cast("boolean"))
        .withColumn("FromBank", col("FromBank").cast("int"))
        .withColumn("ToBank", col("ToBank").cast("int"))
        .withColumn("AmountReceived", col("AmountReceived").cast(DecimalType(15, 2)))
        .withColumn("AmountPaid", col("AmountPaid").cast(DecimalType(15, 2)))
    )
