import sys
import json
import boto3
from botocore.exceptions import ClientError

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame


def get_db_secret():
    secret_name = "historic_data_creds"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response["SecretString"])

    return secret


def load_frame_from_jdbc(
    sparkObject, jdbc_url, user, password, engine, dbtable, schema
):
    if engine == "postgresql":
        driver = "org.postgresql.Driver"
    else:
        return None

    return (
        sparkObject.read.format("jdbc")
        .option("url", jdbc_url)
        .option("driver", driver)
        .option("dbtable", f"(SELECT * from {schema}.{dbtable}) as {dbtable}")
        .option("user", user)
        .option("password", password)
        .load()
    )

args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "OBJECT_NAME", "RUN_ID"]
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

object_name = args.get("OBJECT_NAME")
run_id = args.get("RUN_ID")

# Get db credentials
db_creds = get_db_secret()
host = db_creds.get("host")
user = db_creds.get("username")
password = db_creds.get("password")
port = db_creds.get("port")
database = "historic_data"
schema = "employees_data"
jdbc_url = f"jdbc:postgresql://{host}:{port}/{database}"

# Read table with JDBC
table_frame = load_frame_from_jdbc(
        sparkObject=spark,
        jdbc_url=jdbc_url,
        user=user,
        password=password,
        engine="postgresql",
        dbtable=object_name,
        schema=schema,
    )

table_frame.show(10)

# Write into S3
table_frame_dnf = DynamicFrame.fromDF(table_frame, glueContext, object_name)
glueContext.write_dynamic_frame.from_options(
    frame=table_frame_dnf,
    connection_type="s3",
    format="avro",
    connection_options={"path": f"s3://backup-gcc-data/{object_name}", "partitionKeys": ["run"]},
    transformation_ctx="S3_proc_data",
)


job.commit()
