import sys
import json
import boto3
import psycopg2
from datetime import datetime
from botocore.exceptions import ClientError

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame
from pyspark.sql.functions import to_timestamp, lit, col


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


def load_frame_from_jdbc(sparkObject, jdbc_url, user, password, engine, dbtable, schema):
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

def get_null_dataframe(frame, null_columns):
    # Get dataframe with null values to log
    conditions = [col(column_name).isNull() for column_name in null_columns]

    # Combine conditions using OR operator
    combined_condition = conditions[0]
    for condition in conditions[1:]:
        combined_condition = combined_condition | condition

    # Filter the DataFrame based on the combined condition
    null_frame = frame.filter(combined_condition)
    return null_frame

args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "BUCKET_NAME", "OBJECT_NAME", "RUN_ID"]
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket_name = args.get("BUCKET_NAME")
object_name = args.get("OBJECT_NAME")
run_id = args.get("RUN_ID")

# Get db credentials
db_creds = get_db_secret()
host = db_creds.get("host")
user = db_creds.get("username")
password = db_creds.get("password")
port = db_creds.get("port")
database = "historic_data"

# Read csv
read_frame = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": False,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={"paths": [f"s3://{bucket_name}/{object_name}.csv"]},
    transformation_ctx="reading_csv",
)


if object_name == "departments":
    mappings = [
        ("col0", "string", "id", "bigint"),
        ("col1", "string", "department", "string"),
    ]
    null_columns = ["department"]
elif object_name == "jobs":
    mappings = [
        ("col0", "string", "id", "bigint"),
        ("col1", "string", "job", "string"),
    ]
    null_columns = ["job"]
elif object_name == "hired_employees":
    mappings = [
        ("col0", "string", "id", "bigint"),
        ("col1", "string", "name", "string"),
        ("col2", "string", "datetime", "string"),
        ("col3", "string", "department_id", "bigint"),
        ("col4", "string", "job_id", "bigint"),
    ]
    null_columns = ["name", "datetime", "department_id", "job_id"]
else:
    sys.exit()

# Script generated for node Change Schema
proc_frame = ApplyMapping.apply(
    frame=read_frame,
    mappings=mappings,
    transformation_ctx="schema_mapping",
)

proc_frame = proc_frame.toDF().withColumn("run", lit(run_id))

null_frame = get_null_dataframe(proc_frame, null_columns)
null_frame.show(10)

# Drop null fields for important columns
proc_frame = proc_frame.na.drop(subset=null_columns)

# For hired_employees, check for job and departemnts not found in their corresponding tables
if object_name == "hired_employees":
    proc_frame = proc_frame.withColumn(
        "datetime", to_timestamp("datetime", "yyyy-MM-dd'T'HH:mm:ssX")
    )
    proc_frame = proc_frame.na.drop(subset=null_columns)

    # Read actual data from RDS to check for department and job IDs
    jdbc_url = f"jdbc:postgresql://{host}:{port}/{database}"
    df_actual_jobs = load_frame_from_jdbc(
        sparkObject=spark,
        jdbc_url=jdbc_url,
        user=user,
        password=password,
        engine="postgresql",
        dbtable="jobs",
        schema="employees_data"
    )
    df_actual_jobs = df_actual_jobs.withColumnRenamed("id", "job_id_actual").drop("run")

    df_actual_departments = load_frame_from_jdbc(
        sparkObject=spark,
        jdbc_url=jdbc_url,
        user=user,
        password=password,
        engine="postgresql",
        dbtable="departments",
        schema="employees_data"
    )
    df_actual_departments = df_actual_departments.withColumnRenamed("id", "department_id_actual").drop("run")

    # No matching IDs dataframe
    no_match_jobs_df = proc_frame.join(
        df_actual_jobs, proc_frame.job_id == df_actual_jobs.job_id_actual, how="left_anti"
    )
    no_match_departments_df = proc_frame.join(
        df_actual_departments,
        proc_frame.department_id == df_actual_departments.department_id_actual,
        how="left_anti",
    )
    no_match_df = no_match_jobs_df.union(no_match_departments_df).dropDuplicates()
    no_match_df.show(10)

    # Join with IDs to get only the hired employees with a valid department and job ID
    proc_frame = (
        proc_frame.join(
            df_actual_jobs,
            proc_frame.job_id == df_actual_jobs.job_id_actual,
            how="inner",
        )
        .drop("job_id_actual").drop("job")
    )
    proc_frame = proc_frame.join(
        df_actual_departments,
        proc_frame.department_id == df_actual_departments.department_id_actual,
        how="inner",
    ).drop("department_id_actual").drop("department")

    proc_frame.show(10)


# Write Run dataframe
data = [
    {"run_id": run_id, "process": f"upload_{object_name}", "timestamp": datetime.now()}
]
run_dnf = DynamicFrame.fromDF(spark.createDataFrame(data=data), glueContext, "runs")

# Write run data
connection_options = {
    "url": f"jdbc:postgresql://{host}:{port}/{database}",
    "user": user,
    "password": password,
    "dbtable": "employees_data.runs",
}

glueContext.write_dynamic_frame.from_options(
    frame=run_dnf,
    connection_type="postgresql",
    connection_options=connection_options,
    transformation_ctx="JDBC_run_data",
)

# Write into S3
proc_frame_dnf = DynamicFrame.fromDF(proc_frame, glueContext, object_name)
glueContext.write_dynamic_frame.from_options(
    frame=proc_frame_dnf,
    connection_type="s3",
    format="csv",
    connection_options={"path": "s3://proc-gcc-data", "partitionKeys": ["run"]},
    transformation_ctx="S3_proc_data",
)

# Write into PostgreSQL
proc_frame.rdd.coalesce(10).foreachPartition(
    lambda x: upsert_spark_dataframe(
        x, db_creds, database, "employees_data", object_name
    )
)

job.commit()
