import json
import boto3
import uuid

s3_client = boto3.client('s3')

def split_rows(header, rows, n):
    current_rows = [header]
    file_number = 1
    
    csv_list = []
    for row in rows:
        current_rows.append(row + '\n')  # Add back the newline character
        if len(current_rows) >= n:
            csv_list.append(''.join(current_rows))
            current_rows = [header]
            file_number += 1

    return csv_list

def lambda_handler(event, context):
    try:
        bucket_name = 'raw-gcc-data'
        max_rows_per_file = 1000

        # Parse from the event data
        content_type = event['headers']['Content-Type']
        binary_body = event['body']
        
        # Retrieve the file name from the query parameters
        query_parameters = event.get('queryStringParameters', {})
        object_name = query_parameters.get('object')

        # Error if there is no object_name
        if not object_name:
            response = {
                'statusCode': 400,
                'body': json.dumps("Error, missing object name paramenter")
            }
            return response
        
        # Error if the object_name is not valid
        if object_name not in ["departments", "jobs", "hired_employees"]:
            response = {
                'statusCode': 400,
                'body': json.dumps("Error, Invalid object name paramenter")
            }
            return response
        
        print(f"Processing: {object_name}")

        if object_name == "jobs":
            header = "id,job\n"
        elif object_name =="departments":
            header = "id,department\n"
        elif object_name =="hired_employees":
            header ="id,name,datetime,department_id,job_id\n"
        

        # Split file into chunks of maximum 1000 rows
        rows = binary_body.replace("\r\n", "\n").replace("\r", "\n").split('\n')
        print(f"Number of rows: {len(rows)}")
        list_of_csv = split_rows(header, rows, max_rows_per_file)

        # Store the file in S3
        for index, csv in enumerate(list_of_csv):
            run_id = str(uuid.uuid4())
            s3_client.put_object(
                Bucket=bucket_name,
                Key=f"{object_name}/{run_id}/{index+1}.csv",
                Body=csv,
                ContentType=content_type
            )
        
        response = {
            'statusCode': 200,
            'body': json.dumps('File uploaded successfully')
        }
    except Exception as e:
        print(e)
        response = {
            'statusCode': 500,
            'body': json.dumps('An error occurred: ' + str(e))
        }
    
    return response
