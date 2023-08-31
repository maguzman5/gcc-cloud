import json
import boto3
import uuid

glue = boto3.client('glue')

def lambda_handler(event, context):
    s3_event = event["Records"][0]["s3"]
    bucket_name = s3_event["bucket"]["name"]
    object_name = s3_event["object"]["key"].split(".")[0]
    
    run_uuid = str(uuid.uuid4())
    gluejobname="gcc_insert_job"

    try:
        runId = glue.start_job_run(JobName=gluejobname, Arguments={
        '--BUCKET_NAME': bucket_name,
        '--OBJECT_NAME': object_name,
        '--RUN_ID': run_uuid
    })
        status = glue.get_job_run(JobName=gluejobname, RunId=runId['JobRunId'])
        print("Job Status : ", status['JobRun']['JobRunState'])
    except Exception as e:
        print(e)
        raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps(f"{gluejobname}: Running with {object_name}")
    }
