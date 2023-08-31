data "archive_file" "gcc_upload_csv_zip" {
  type        = "zip"
  source_file = "../scripts/lambda/gcc_upload_csv/main.py"
  output_path = "../scripts/lambda/gcc_upload_csv/main.zip"
}

data "archive_file" "gcc_trigger_glue_zip" {
  type        = "zip"
  source_file = "../scripts/lambda/gcc_trigger_glue/main.py"
  output_path = "../scripts/lambda/gcc_trigger_glue/main.zip"
}

data "archive_file" "gcc_trigger_backup_zip" {
  type        = "zip"
  source_file = "../scripts/lambda/gcc_trigger_backup/main.py"
  output_path = "../scripts/lambda/gcc_trigger_backup/main.zip"
}