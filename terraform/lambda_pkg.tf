data "archive_file" "gcc_upload_csv_zip" {
  type        = "zip"
  source_file = "../scripts/lambda/gcc_upload_csv/main.py"
  output_path = "../scripts/lambda/gcc_upload_csv/main.zip"
}