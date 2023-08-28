resource "aws_lambda_function" "upload_csv_lambda" {
  function_name    = var.upload_csv_function_name
  filename         = data.archive_file.gcc_upload_csv_zip.output_path
  source_code_hash = data.archive_file.gcc_upload_csv_zip.output_base64sha256

  role       = aws_iam_role.gcc_upload_csv_exec_role.arn
  handler    = "main.lambda_handler"
  runtime    = "python3.10"
  depends_on = [data.archive_file.gcc_upload_csv_zip]

  tags = {
    project = "GCC"
  }
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.upload_csv_lambda.function_name}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.gcc_api.execution_arn}/*/*"
}