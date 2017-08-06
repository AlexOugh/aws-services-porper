#!/bin/sh

# Currently, the swagger.yaml does NOT support to set AWS Account Id and Region dynamically
# so creating a stack in a different accounts/regions from where this template and artifacts are shared is failing
# until then, do NOT set "S3_SHARED_BUCKET_NAME"
if [ "$S3_SHARED_BUCKET_NAME" != "" ];
then
  # make lambda zip file public
  aws s3 cp `cat samTemplate.yaml | shyaml get-value Resources.ProxyFunction.Properties.CodeUri` s3://$S3_SHARED_BUCKET_NAME  --acl public-read
  # make swagger file public
  aws s3 cp `cat samTemplate.yaml | shyaml get-value Resources.ApiGatewayApi.Properties.DefinitionUri` s3://$S3_SHARED_BUCKET_NAME  --acl public-read
  # upload template file
  aws s3 cp ./samTemplate.yaml s3://$S3_SHARED_BUCKET_NAME/samTemplate.yaml --acl public-read
fi
