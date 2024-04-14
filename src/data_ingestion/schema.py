from pyspark.sql.types import StringType, StructField, StructType

input_schema = StructType(
    [
        StructField("Timestamp", StringType(), True),
        StructField("From Bank", StringType(), True),
        StructField("Account", StringType(), True),
        StructField("To Bank", StringType(), True),
        StructField("Amount Received", StringType(), True),
        StructField("Receiving Currency", StringType(), True),
        StructField("Amount Paid", StringType(), True),
        StructField("Payment Currency", StringType(), True),
        StructField("Payment Format", StringType(), True),
        StructField("Is Laundering", StringType(), True),
    ],
)
