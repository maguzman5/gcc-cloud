variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for Terraform Provider"
}

variable "aws_profile" {
  type        = string
  default     = "personal"
  description = "AWS profile for Terraform Provider"
}


variable "raw_bucket_name" {
  type        = string
  default     = "raw-gcc-data"
  description = "AWS S3 bucket to store raw data for GCC"
}

variable "proc_bucket_name" {
  type        = string
  default     = "proc-gcc-data"
  description = "AWS S3 bucket to store processed data for GCC"
}

variable "backup_bucket_name" {
  type        = string
  default     = "backup-gcc-data"
  description = "AWS S3 bucket to store AVRO backups for GCC"
}

variable "upload_csv_function_name" {
  type        = string
  default     = "gcc_upload_csv"
  description = "AWS upload lambda function name"
}

variable "trigger_glue_function_name" {
  type        = string
  default     = "gcc_trigger_glue"
  description = "AWS trigger glue lambda function name"
}

variable "trigger_backup_function_name" {
  type        = string
  default     = "gcc_trigger_backup"
  description = "AWS trigger backup lambda function name"
}

variable "trigger_restore_function_name" {
  type        = string
  default     = "gcc_trigger_restore"
  description = "AWS trigger restore lambda function name"
}

variable "api_name" {
  type        = string
  default     = "API_GCC"
  description = "AWS REST API name in API Gateway"
}

variable "insert_glue_job_name" {
  type    = string
  default = "gcc_insert_job"
}

variable "backup_glue_job_name" {
  type    = string
  default = "gcc_backup_job"
}

variable "restore_glue_job_name" {
  type    = string
  default = "gcc_restore_job"
}

variable "cloudwatch_group_name" {
  type    = string
  default = "gcc-runs"
}
