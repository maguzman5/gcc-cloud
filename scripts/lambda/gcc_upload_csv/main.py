import json
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Parse from the event data
        content_type = event['headers']['Content-Type']
        binary_body = event['body']
        
        # Retrieve the file name from the query parameters
        query_parameters = event.get('queryStringParameters', {})
        filename = query_parameters.get('filename', 'uploaded_file')
        
        # Store the file in S3
        bucket_name = 'raw-data-gcc'
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=binary_body,
            ContentType=content_type
        )
        
        response = {
            'statusCode': 200,
            'body': json.dumps('File uploaded and processed successfully')
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps('An error occurred: ' + str(e))
        }
    
    return response
