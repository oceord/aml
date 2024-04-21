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
        json_df.select([col(x).alias(x.replace(" ", "_")) for x in json_df.columns])
        .withColumn("Timestamp", to_timestamp(col("Timestamp"), "yyyy/MM/dd HH:mm"))
        .withColumn("From_Bank", col("From_Bank").cast("int"))
        .withColumn("To_Bank", col("To_Bank").cast("int"))
        .withColumn("Amount_Received", col("Amount_Received").cast(DecimalType(15, 2)))
        .withColumn("Amount_Paid", col("Amount_Paid").cast(DecimalType(15, 2)))
        .withColumn("Is_Laundering", col("Is_Laundering").cast("boolean"))
    )
