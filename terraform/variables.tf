variable aws_region {
    type = string
    default="us-east-1"
    description = "AWS region for Terraform Provider"
}

variable aws_profile {
    type = string
    default="personal"
    description = "AWS profile for Terraform Provider"
}