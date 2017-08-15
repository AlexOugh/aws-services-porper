#!/bin/sh

# *** Prerequisite:
# The bucket specified in "S3_SHARED_BUCKET_NAME" must allow the account that copies its artifact by specifying this policy in the bucket's Bucket Policy
# {
#    "Version": "2012-10-17",
#    "Statement": [
#        {
#            "Sid": "111",
#            "Effect": "Allow",
#            "Principal": {
#                "AWS": "arn:aws:iam::<Account_Id_that_copies_its_artifact>:root"
#            },
#            "Action": "s3:PutObject",
#            "Resource": "arn:aws:s3:::<$S3_SHARED_BUCKET_NAME>/*"
#        }
#    ]
# }


# Needs 2 steps to execute commands Manually
# 1. Add "S3_SHARED_BUCKET_NAME" in "Environment variables" of CodeBuild project
# 2. Add below policy in the CodeBuild's role policy document
# {
#   "Action": [
#     "s3:*"
#   ],
#   "Resource": [
#     "arn:aws:s3:::<$S3_SHARED_BUCKET_NAME>/*"
#   ],
#   "Effect": "Allow"
# }

# OR use "codepipeline_with_shared_bucket.yaml" cloudformation when building its pipeline stack


if [ "$S3_SHARED_BUCKET_NAME" != "" ];
then
  # make lambda zip file public
  aws s3 cp `cat samTemplate.yaml | shyaml get-value Resources.ProxyFunction.Properties.CodeUri` s3://$S3_SHARED_BUCKET_NAME  --acl public-read
  # upload template file
  aws s3 cp ./samTemplate.yaml s3://$S3_SHARED_BUCKET_NAME/samTemplate.yaml --acl public-read
fi
