
source .env.local

#cd src; pip install ../../porper-core/dist/porper-0.4.0-py2.py3-none-any.whl -t ./lib --upgrade; cd ..
#cd src; pip install porper -t ./lib; cd ..

sed -i 1 "s/AWS::REGION/$AWS_DEFAULT_REGION/g" swagger.yaml
sed -i 2 "s/AWS::ACCOUNT_ID/$AWS_ACCOUNT_ID/g" swagger.yaml


aws cloudformation package \
   --template-file ./template.yaml \
   --s3-bucket $S3_BUCKET_NAME \
   --output-template-file samTemplate.yaml


mv swagger.yaml1 swagger.yaml
rm swagger.yaml2


aws cloudformation deploy --template-file ./samTemplate.yaml \
  --capabilities CAPABILITY_IAM \
  --stack-name SungardAS-aws-services-porper-afactor \
  --parameter-overrides RedirectUri=$REDIRECT_URI \
    GoogleTokeninfoEndpoint=$GOOGLE_TOKEN_INFO_ENDPOINT \
    GoogleClientId=$GOOGLE_CLIENT_ID \
    GoogleClientSecret=$GOOGLE_CLIENT_SECRET \
    SsoHost=$SSO_HOST \
    SsoClientId=$SSO_CLIENT_ID \
    SsoClientSecret=$SSO_CLIENT_SECRET \
    GithubAuthEndpoint=$GITHUB_AUTH_ENDPOINT \
    GithubApiEndpoint=$GITHUB_API_ENDPOINT \
    GithubClientId=$GITHUB_CLIENT_ID \
    GithubClientSecret=$GITHUB_CLIENT_SECRET \
    SlackAuthEndpoint=$SLACK_AUTH_ENDPOINT \
    SlackApiEndpoint=$SLACK_API_ENDPOINT \
    SlackClientId=$SLACK_CLIENT_ID \
    SlackClientSecret=$SLACK_CLIENT_SECRET \
    SlackSlashCommandToken=$SLACK_SLASH_COMMAND_TOKEN \
    ReadCapacityUnit=$READ_CAPACITY_UNIT \
    WriteCapacityUnit=$WRITE_CAPACITY_UNIT \
    PorperLambdaLayerARN=$PORPER_LAMBDA_LAYER_ARN


rm samTemplate.yaml
