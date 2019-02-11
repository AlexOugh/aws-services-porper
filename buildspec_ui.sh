
source .env.local

aws cloudformation deploy --template-file ./template.ui.yaml \
  --capabilities CAPABILITY_IAM \
  --stack-name SungardAS-aws-services-porper-ui
