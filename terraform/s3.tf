resource "aws_s3_bucket" "raw_bucket" {
  bucket = var.raw_bucket_name

  tags = {
    project = "GCC"
  }
}

resource "aws_s3_bucket" "proc_bucket" {
  bucket = var.proc_bucket_name

  tags = {
    project = "GCC"
  }
}

resource "aws_s3_bucket" "backup_bucket" {
  bucket = var.backup_bucket_name

  tags = {
    project = "GCC"
  }
}
