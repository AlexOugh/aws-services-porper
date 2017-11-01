
# Porper Services

API Gateway and Lambda functions to provide the interfaces with Porper

![aws-services][aws-services-image]

## How To Setup a CodePipeline

Template : "./codepipeline.yaml"

Input Parameter Values

- GitHubSourceRepositoryOwner: SungardAS

- GitHubSourceRepositoryName: aws-services-porper

- GitHubSourceRepositoryBranch: master

- GitHubPersonalAccessToken:

  Access Token for CodeBuild to access to the this Github repository. (See here to find how to generate the access token)

- GoogleTokeninfoEndpoint: Endpoint url to confirm Google tokens

- SsoHost:

- SsoUser:

- SsoPassword:

- SsoRedirectUri:

- GithubAuthEndpoint: Endpoint url to confirm GitHub tokens

- GithubApiEndpoint: GitHub API Endpoint url

- GithubClientId: GitHub Client Id

- GithubClientSecret: GitHub Client Secret

- GithubRedirectUri: GitHub Redirect Uri

- SlackAuthEndpoint: Endpoint url to confirm Slack tokens

- SlackApiEndpoint: Slack API Endpoint url

- SlackClientId: Slack Client Id

- SlackClientSecret: Slack Client Secret

- SlackSlashCommandToken: Slack Token for Slash Command

- ReadCapacityUnit: Read Capacity Unit for DynamoDB Tables

- WriteCapacityUnit: Write Capacity Unit for DynamoDB Tables

- ProjectImage: aws/codebuild/python:2.7.12

- S3SharedBucketName:

  Please see './s3.sh' to find out how to prepare the shared bucket
  (Only need the to do the first one. The second 2 steps are configured during this stack's creation)


## Sungard Availability Services | Labs
[![Sungard Availability Services | Labs][labs-image]][labs-github-url]

This project is maintained by the Labs team at [Sungard Availability
Services][sungardas-url]

GitHub: [https://sungardas.github.io][sungardas-github-url]

Blog: [http://blog.sungardas.com/CTOLabs/][sungardaslabs-blog-url]

[porper-api-url]: https://github.com/SungardAS/porper-api
[labs-github-url]: https://sungardas.github.io
[labs-image]: https://raw.githubusercontent.com/SungardAS/repo-assets/master/images/logos/sungardas-labs-logo-small.png
[sungardas-github-url]: https://sungardas.github.io
[sungardas-url]: http://sungardas.com
[sungardaslabs-blog-url]: http://blog.sungardas.com/CTOLabs/
