resource "aws_api_gateway_rest_api" "gcc_api" {
  name        = var.api_name
  description = "API Gateway for GCC"
}

# Upload Endpoint

resource "aws_api_gateway_resource" "uploadResource" {
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  parent_id   = aws_api_gateway_rest_api.gcc_api.root_resource_id
  path_part   = "upload"
}

resource "aws_api_gateway_method" "executeUpload" {
  rest_api_id   = aws_api_gateway_rest_api.gcc_api.id
  resource_id   = aws_api_gateway_resource.uploadResource.id
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "uploadIntegration" {
  rest_api_id             = aws_api_gateway_rest_api.gcc_api.id
  resource_id             = aws_api_gateway_resource.uploadResource.id
  http_method             = aws_api_gateway_method.executeUpload.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upload_csv_lambda.invoke_arn
}

resource "aws_api_gateway_method_response" "uploadResponse" {
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  resource_id = aws_api_gateway_resource.uploadResource.id
  http_method = aws_api_gateway_method.executeUpload.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "uploadIntegrationResponse" {
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  resource_id = aws_api_gateway_resource.uploadResource.id
  http_method = aws_api_gateway_method.executeUpload.http_method
  status_code = aws_api_gateway_method_response.uploadResponse.status_code


  response_templates = {
    "application/json" = jsonencode({ message = "Success" })
  }

  depends_on = [
    aws_api_gateway_integration.uploadIntegration
  ]
}

# Backup 

resource "aws_api_gateway_resource" "backupResource" {
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  parent_id   = aws_api_gateway_rest_api.gcc_api.root_resource_id
  path_part   = "backup"
}

resource "aws_api_gateway_method" "executeBackup" {
  rest_api_id   = aws_api_gateway_rest_api.gcc_api.id
  resource_id   = aws_api_gateway_resource.backupResource.id
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "backupIntegration" {
  rest_api_id             = aws_api_gateway_rest_api.gcc_api.id
  resource_id             = aws_api_gateway_resource.backupResource.id
  http_method             = aws_api_gateway_method.executeBackup.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.trigger_backup_lambda.invoke_arn
}

resource "aws_api_gateway_method_response" "backupResponse" {
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  resource_id = aws_api_gateway_resource.backupResource.id
  http_method = aws_api_gateway_method.executeBackup.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "backupIntegrationResponse" {
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  resource_id = aws_api_gateway_resource.backupResource.id
  http_method = aws_api_gateway_method.executeBackup.http_method
  status_code = aws_api_gateway_method_response.backupResponse.status_code


  response_templates = {
    "application/json" = jsonencode({ message = "Success" })
  }

  depends_on = [
    aws_api_gateway_integration.backupIntegration
  ]
}

# Deploy

resource "aws_api_gateway_deployment" "deployUpload" {
  depends_on  = [aws_api_gateway_integration.uploadIntegration, aws_api_gateway_integration.backupIntegration]
  rest_api_id = aws_api_gateway_rest_api.gcc_api.id
  stage_name  = "dev"

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.uploadResource,
      aws_api_gateway_method.executeUpload,
      aws_api_gateway_integration.uploadIntegration,
      aws_api_gateway_resource.backupResource,
      aws_api_gateway_method.executeBackup,
      aws_api_gateway_integration.backupIntegration,
    ]))
  }

}
