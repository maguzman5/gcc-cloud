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
  default     = "hackup-gcc-data"
  description = "AWS S3 bucket to store AVRO backups for GCC"
}

variable "upload_csv_function_name" {
    type = string
    default = "gcc_upload_csv"
    description = "AWS upload lambda function name"
}
