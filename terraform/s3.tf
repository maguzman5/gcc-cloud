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

resource "aws_s3_bucket" "scripts_bucket" {
  bucket = "gcc-scripts-bucket"

  tags = {
    project = "GCC"
  }
}

resource "aws_s3_object" "upload_py_files" {
  for_each   = fileset("../scripts/glue", "*.py")
  bucket     = aws_s3_bucket.scripts_bucket.id
  key        = "glue/${each.value}"
  source     = "../scripts/glue/${each.value}"
  etag       = filemd5("../scripts/glue/${each.value}")
  depends_on = [aws_s3_bucket.scripts_bucket]
}

