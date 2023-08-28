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
  name = "GCCUploadCSVS3Policy"
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
        }
      ]
    }
  )
}

# resource "aws_iam_role_policy_attachment" "gcc_upload_csv_attach" {
#   role       = aws_iam_role.gcc_upload_csv_exec_role.name
#   policy_arn = aws_iam_role_policy.gcc_upload_csv_policy.arn
# }
