resource "aws_glue_job" "insert_job" {
  name         = var.insert_glue_job_name
  role_arn     = "arn:aws:iam::938070615203:role/AWSGlueServiceRole-GCC"
  glue_version = "4.0"

  worker_type       = "G.1X"
  number_of_workers = 2

  execution_property {
    max_concurrent_runs = 2
  }
  default_arguments = {
    "--BUCKET_NAME"                      = "",
    "--OBJECT_NAME"                      = "",
    "--RUN_ID"                           = "",
    "--job-language"                     = "python",
    "--job-bookmark-option"              = "job-bookmark-enable",
    "--enable-spark-ui"                  = "true",
    "--enable-metrics"                   = "true",
    "--enable-continuous-cloudwatch-log" = "true",
    "--enable-glue-datacatalog"          = "true",
    "--enable-job-insights"              = "false",
  }

  command {
    script_location = "s3://gcc-scripts-bucket/glue/gcc_insert.py"
    python_version  = 3
  }

  connections = ["historic-data-conn"]

  tags = {
    project = "GCC"
  }
}

