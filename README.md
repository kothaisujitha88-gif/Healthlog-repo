# HealthLog

A simple serverless web app for logging personal health readings once a month: fasting sugar, after-meal sugar, blood pressure (systolic/diastolic) and weight.

## Features

- Sign up and sign in
- Save a new entry
- View your entry history
- Edit and delete entries
- Automatic "next entry due" banner (the 1st of the month after your latest entry)

## Built with

- Amazon S3 and CloudFront: frontend hosting
- Amazon Cognito: sign-up and sign-in
- Amazon API Gateway (HTTP API): backend API, protected by a Cognito authorizer
- AWS Lambda (Python): backend logic
- Amazon DynamoDB: data storage
- AWS IAM: roles and permissions

All resources were created by hand in the AWS console.

## Project status

The app works end to end when run locally. CloudFront hosting is pending AWS account verification.

## Run it locally

1. Open the `frontend` folder.
2. Serve it on port 3000 and open http://localhost:3000 in your browser.
3. Put your own AWS values in the `frontend/index.html` placeholders: `<APP_CLIENT_ID>`, `<COGNITO_DOMAIN_PREFIX>` and `<API_URL>`.

## Documentation

See [docs/architecture.md](docs/architecture.md) for the architecture and service settings.

## Folder structure

- `frontend/`: the web page (index.html)
- `lambda/`: the Lambda function code
- `docs/`: architecture document and images