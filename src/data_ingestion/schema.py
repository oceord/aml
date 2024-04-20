from pyspark.sql.types import StringType, StructField, StructType

FROM_ACCOUNT_INDEX = 2

input_schema = StructType(
    [
        StructField("Timestamp", StringType(), True),
        StructField("From Bank", StringType(), True),
        StructField("From Account", StringType(), True),
        StructField("To Bank", StringType(), True),
        StructField("To Account", StringType(), True),
        StructField("Amount Received", StringType(), True),
        StructField("Receiving Currency", StringType(), True),
        StructField("Amount Paid", StringType(), True),
        StructField("Payment Currency", StringType(), True),
        StructField("Payment Format", StringType(), True),
        StructField("Is Laundering", StringType(), True),
    ],
)
