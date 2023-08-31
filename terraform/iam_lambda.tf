
# upload csv role
resource "aws_iam_role" "gcc_upload_csv_exec_role" {
  name = "GCCUploadCSVExecRole"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
}

resource "aws_iam_role_policy" "gcc_upload_csv_policy" {
  name = "GCCUploadCSVPolicy"
  role = aws_iam_role.gcc_upload_csv_exec_role.id

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:GetBucketLocation",
            "s3:ListAllMyBuckets"
          ],
          "Resource" : "arn:aws:s3:::*"
        },
        {
          "Effect" : "Allow",
          "Action" : "s3:*",
          "Resource" : [
            "arn:aws:s3:::${aws_s3_bucket.raw_bucket.id}",
            "arn:aws:s3:::${aws_s3_bucket.raw_bucket.id}/*"
          ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
      ]
    }
  )
}

# Trigger glue exec
resource "aws_iam_role" "gcc_trigger_glue_exec_role" {
  name = "GCCTriggerGlueExecRole"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
}

resource "aws_iam_role_policy" "gcc_trigger_glue_policy" {
  name = "GCCTriggerGluePolicy"
  role = aws_iam_role.gcc_trigger_glue_exec_role.id

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:GetBucketLocation",
            "s3:ListAllMyBuckets"
          ],
          "Resource" : "arn:aws:s3:::*"
        },
        {
          "Effect" : "Allow",
          "Action" : "s3:*",
          "Resource" : [
            "arn:aws:s3:::${aws_s3_bucket.raw_bucket.id}",
            "arn:aws:s3:::${aws_s3_bucket.raw_bucket.id}/*"
          ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
      ]
    }
  )
}

# Backup exec role
resource "aws_iam_role" "gcc_trigger_backup_exec_role" {
  name = "GCCTriggerBackupExecRole"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    }
  )
}

resource "aws_iam_role_policy" "gcc_trigger_backup_policy" {
  name = "GCCTriggerGluePolicy"
  role = aws_iam_role.gcc_trigger_backup_exec_role.id

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:GetBucketLocation",
            "s3:ListAllMyBuckets"
          ],
          "Resource" : "arn:aws:s3:::*"
        },
        {
          "Effect" : "Allow",
          "Action" : "s3:*",
          "Resource" : [
            "arn:aws:s3:::${aws_s3_bucket.backup_bucket.id}",
            "arn:aws:s3:::${aws_s3_bucket.backup_bucket.id}/*"
          ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
      ]
    }
  )
}