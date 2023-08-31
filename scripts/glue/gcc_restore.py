import sys
import json
import boto3
import psycopg2
from datetime import datetime
from botocore.exceptions import ClientError

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import lit
from awsglue.context import GlueContext
from awsglue.job import Job


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


def process_row(row, cursor, schema, table):
    db_table = f"{schema}.{table}"
    if table == "jobs":
        job_id = row.__getitem__("id")
        job = row.__getitem__("job").replace("'", "''")
        run_id = row.__getitem__("run")
        sql_query = f"""INSERT INTO {db_table} (id, job, run) VALUES ('{job_id}', '{job}', '{run_id}') ON CONFLICT (id) DO UPDATE SET id='{job_id}', job='{job}', run='{run_id}'"""
    elif table == "departments":
        department_id = row.__getitem__("id")
        department = row.__getitem__("department").replace("'", "''")
        run_id = row.__getitem__("run")
        sql_query = f"""INSERT INTO {db_table} (id, department, run) VALUES ('{department_id}', '{department}', '{run_id}') ON CONFLICT (id) DO UPDATE SET id='{department_id}', department='{department}', run='{run_id}'"""
    elif table == "hired_employees":
        he_id = row.__getitem__("id")
        name = row.__getitem__("name").replace("'", "''")
        datetime = row.__getitem__("datetime")
        run_id = row.__getitem__("run")
        department_id = row.__getitem__("department_id")
        job_id = row.__getitem__("job_id")
        sql_query = f"""INSERT INTO {db_table} (id, name, datetime, run, department_id, job_id) VALUES ('{he_id}', '{name}', '{datetime}', '{run_id}', '{department_id}', '{job_id}') ON CONFLICT (id) DO UPDATE SET id='{he_id}', name='{name}', datetime='{datetime}', run='{run_id}', department_id='{department_id}', job_id='{job_id}'"""
    else:
        return None

    cursor.execute(sql_query)


def upsert_spark_dataframe(partition, db_creds, database, schema, table):
    host = db_creds.get("host")
    user = db_creds.get("username")
    password = db_creds.get("password")
    port = db_creds.get("port")

    db_conn = psycopg2.connect(
        host=host, user=user, password=password, database=database, port=port
    )

    cursor = db_conn.cursor()

    for row in partition:
        process_row(row=row, cursor=cursor, schema=schema, table=table)

    db_conn.commit()
    cursor.close()
    db_conn.close()

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

# Read csv
read_frame = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="avro",
    connection_options={"paths": [f"s3://backup-gcc-data/{object_name}/run={run_id}"]},
    transformation_ctx="reading_avro",
)

proc_frame = read_frame.toDF().withColumn("run", lit(run_id))
proc_frame.show(10)

# Write into PostgreSQL
proc_frame.rdd.coalesce(10).foreachPartition(
    lambda x: upsert_spark_dataframe(
        x, db_creds, database, schema, object_name
    )
)

job.commit()
