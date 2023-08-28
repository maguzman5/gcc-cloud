# GCC Cloud

This repo should contain all the insfrastructure to build the GCC data pipelines in AWS. 

## To Do
- Create S3 buckets for:
    - Raw data
    - Processed data
    - Backups
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