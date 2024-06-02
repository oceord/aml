from pyspark.sql import SparkSession
from pyspark.sql.functions import sum

SPARK_APP_NAME = "MapRed_AccountTotalIn"
SPARK_MASTER = "local[*]"

HDFS_JSON_FOLDER = "hdfs://localhost/aml/raw/events/json"

spark = SparkSession.builder.appName(SPARK_APP_NAME).master(SPARK_MASTER).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

data_df = spark.read.json(HDFS_JSON_FOLDER)
agg_df = data_df.groupBy("From_Bank", "From_Account").agg(
    sum("Amount_Paid").alias("Total_Paid"),
)

agg_df.show()
