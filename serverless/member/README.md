# Member

## Required Local File To Deploy

`env.json` must be in this folder locally since it contains the environment variables and `.gitignore` should ignore it when pushing to git

`serverless deploy` will know to read from this file when deploying

```
{
  "EMAIL_SENDER": EMAIL,
  "EMAIL_PASSWORD": EMAIL_PASSWORD,
  "API_ENDPOINT": AWS_ENDPOINT
}
```

`EMAIL_SENDER` and `EMAIL_PASSWORD` are the credentials for the SMTP email sender

`API_ENDPOINT` is the base url (`https://******.execute-api.us-east-1.amazonaws.com/`) for the member API Gateway
