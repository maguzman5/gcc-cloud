# GCC Cloud

This repo should contain all the insfrastructure to build the GCC data pipelines in AWS. 

## How to upload a file

To upload a file to `raw` S3 bucket, you have to execute a POST request to the API URL in the `/upload` endpoint, using the following curl example:
```
curl --location '<rest_api_url>/dev/upload?filename=<filename_csv_file>' \
--header 'Content-Type: text/csv' \
--data '<csv_file_location>'
```

then the file will be uploaded into the S3 bucket with the filename specified in the query parameters

## To Do
- ~~Create S3 buckets for:~~
    - ~~Raw data~~
    - ~~Processed data~~
    - ~~Backups~~
- Create API Gateway with:
    - `/upload` endpoint
    - `/backup` endpoint
    - `/restore` endpoint
- Lambda functions to:
    - Upload CSV files through API Gateway POST request. Also can check some validations
    - Trigger a Glue job to execute the insertion to the database
- Glue jobs:
    - Insertion to the RDS database
    - Backup single table from the RDS database
    - Restore single table to the RDS database
- Create Cloudwatch group and logs to monitor the pipeline