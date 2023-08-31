import json
import boto3

glue = boto3.client('glue')

def lambda_handler(event, context):
    s3_event = event["Records"][0]["s3"]
    bucket_name = s3_event["bucket"]["name"]
    object_key = s3_event["object"]["key"]
    object_key_elements = object_key.split("/")

    run_id = object_key_elements[1]
    object_name = object_key_elements[0]
    print(f"File being processed: {object_key_elements}")
    
    gluejobname="gcc_insert_job"

    try:
        runId = glue.start_job_run(JobName=gluejobname, Arguments={
        '--BUCKET_NAME': bucket_name,
        '--OBJECT_KEY': object_key,
        '--OBJECT_NAME': object_name,
        '--RUN_ID': run_id
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
