import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame
from pyspark.sql.functions import to_timestamp, lit
from datetime import datetime

args = getResolvedOptions(sys.argv, ["JOB_NAME", "BUCKET_NAME", "OBJECT_NAME", "RUN_ID"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket_name = args.get("BUCKET_NAME")
object_name = args.get("OBJECT_NAME")
run_id = args.get("RUN_ID")

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
elif object_name == "jobs":
    mappings = [
        ("col0", "string", "id", "bigint"),
        ("col1", "string", "job", "string"),
        ]
elif object_name == "hired_employees":
    mappings = [
        ("col0", "string", "id", "bigint"),
        ("col1", "string", "name", "string"),
        ("col2", "string", "datetime", "string"),
        ("col3", "string", "department_id", "bigint"),
        ("col4", "string", "job_id", "bigint"),
        ]
else:
    sys.exit()
    
# Script generated for node Change Schema
proc_frame = ApplyMapping.apply(
    frame=read_frame,
    mappings=mappings,
    transformation_ctx="schema_mapping",
)

proc_frame = DynamicFrame.fromDF(proc_frame.toDF().withColumn("run", lit(run_id)), glueContext, object_name)

# Drop null fields for the hired employees table. It requires the IDs of jobs and departments as foreign keys
if object_name =="hired_employees":
    df = proc_frame.toDF().withColumn("datetime", to_timestamp("datetime", "yyyy-MM-dd'T'HH:mm:ssX"))
    df = df.na.drop(subset=["job_id", "department_id", "datetime"])
    proc_frame = DynamicFrame.fromDF(df, glueContext, object_name)


# Write Run dataframe
# data = [{
#     "run_id": run_id,
#     "process": f"upload_{object_name}",
#     "timestamp": datetime.now()
# }]
# run_df = spark.createDataFrame(data=data, schema = ["run_id", "process", "timestamp"])
# run_dnf = DynamicFrame.fromDF(run_df, glueContext, "runs")
# glueContext.write_dynamic_frame.from_catalog(
#     frame=run_dnf,
#     database="historic_data",
#     table_name=f"historic_data_employees_data_runs",
#     transformation_ctx="RDS_run_id",
# )

# Write into S3
glueContext.write_dynamic_frame.from_options(
    frame=proc_frame,
    connection_type="s3",
    format="csv",
    connection_options={"path": "s3://proc-gcc-data", "partitionKeys": ["run"]},
    transformation_ctx="S3_proc_data",
)

# Write into PostgreSQL
glueContext.write_dynamic_frame.from_catalog(
    frame=proc_frame,
    database="historic_data",
    table_name=f"historic_data_employees_data_{object_name}",
    transformation_ctx="RDS_proc_data",
)

job.commit()
