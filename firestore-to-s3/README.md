# Firestore to S3 Exporter

This package handles the export of data from Firestore to S3. It is designed to be deployed as an AWS Lambda function.

## Dependencies

- Python 3.13.4
- boto3 >= 1.38.33
- firebase-admin >= 6.9.0
- pytest >= 8.4.0
- pytz >= 2025.2

## Development

This project uses Poetry for dependency management. To get started:

1. Install Poetry
2. Run `poetry install` to install dependencies
3. Run `poetry build` to build the package

## Deployment

The package is automatically built and deployed to S3 via GitHub Actions when changes are pushed to the main branch.
