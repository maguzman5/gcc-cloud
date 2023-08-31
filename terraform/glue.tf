resource "aws_glue_job" "insert_job" {
  name         = var.insert_glue_job_name
  role_arn     = "arn:aws:iam::938070615203:role/AWSGlueServiceRole-GCC"
  glue_version = "4.0"

  worker_type       = "G.1X"
  number_of_workers = 2

  execution_property {
    max_concurrent_runs = 5
  }
  default_arguments = {
    "--BUCKET_NAME"                      = "",
    "--OBJECT_KEY"                       = "",
    "--OBJECT_NAME"                      = "",
    "--RUN_ID"                           = "",
    "--job-language"                     = "python",
    "--job-bookmark-option"              = "job-bookmark-disable",
    "--enable-spark-ui"                  = "true",
    "--enable-metrics"                   = "true",
    "--enable-continuous-cloudwatch-log" = "true",
    "--enable-glue-datacatalog"          = "true",
    "--enable-job-insights"              = "false",
    "--additional-python-modules"        = "psycopg2-binary==2.9.7"
    # "--extra-py-files"                   = "s3://${aws_s3_bucket.scripts_bucket.id}/deps/glue_deps.zip"
  }

  command {
    script_location = "s3://gcc-scripts-bucket/glue/gcc_insert.py"
    python_version  = 3
  }

  connections = []

  tags = {
    project = "GCC"
  }
}

resource "aws_glue_job" "backup_job" {
  name         = var.backup_glue_job_name
  role_arn     = "arn:aws:iam::938070615203:role/AWSGlueServiceRole-GCC"
  glue_version = "4.0"

  worker_type       = "G.1X"
  number_of_workers = 2

  execution_property {
    max_concurrent_runs = 2
  }
  default_arguments = {
    "--OBJECT_NAME"                      = "",
    "--RUN_ID"                           = "",
    "--job-language"                     = "python",
    "--job-bookmark-option"              = "job-bookmark-disable",
    "--enable-spark-ui"                  = "true",
    "--enable-metrics"                   = "true",
    "--enable-continuous-cloudwatch-log" = "true",
    "--enable-glue-datacatalog"          = "true",
    "--enable-job-insights"              = "false"
  }

  command {
    script_location = "s3://gcc-scripts-bucket/glue/gcc_backup.py"
    python_version  = 3
  }

  connections = []

  tags = {
    project = "GCC"
  }
}


resource "aws_glue_job" "restore_job" {
  name         = var.restore_glue_job_name
  role_arn     = "arn:aws:iam::938070615203:role/AWSGlueServiceRole-GCC"
  glue_version = "4.0"

  worker_type       = "G.1X"
  number_of_workers = 2

  execution_property {
    max_concurrent_runs = 2
  }
  default_arguments = {
    "--OBJECT_NAME"                      = "",
    "--RUN_ID"                           = "",
    "--job-language"                     = "python",
    "--job-bookmark-option"              = "job-bookmark-disable",
    "--enable-spark-ui"                  = "true",
    "--enable-metrics"                   = "true",
    "--enable-continuous-cloudwatch-log" = "true",
    "--enable-glue-datacatalog"          = "true",
    "--enable-job-insights"              = "false",
    "--additional-python-modules"        = "psycopg2-binary==2.9.7"
  }

  command {
    script_location = "s3://gcc-scripts-bucket/glue/gcc_restore.py"
    python_version  = 3
  }

  connections = []

  tags = {
    project = "GCC"
  }
}
