import json
import boto3
import uuid

glue = boto3.client('glue')

def lambda_handler(event, context):
    args = json.loads(event["body"])
    run_id = str(uuid.uuid4())

    object_name = args.get("object")

    print(f"Backup: {object_name}")
    
    gluejobname="gcc_backup_job"

    try:
        runId = glue.start_job_run(JobName=gluejobname, Arguments={
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
