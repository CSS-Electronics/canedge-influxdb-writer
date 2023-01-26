# AWS Lambda Automation

AWS Lambda functions are a smart way to auto-execute code on every log file upload.

Below we describe how you can set up an AWS Lambda function to automatically run the script when a new log file is uploaded.

----

## Before you deploy

- Test that your InfluxDB/Grafana setup works with the sample data
- Test that your setup works with your own data/server when manually running the script from your PC
- Ensure that the S3 credentials in your `inputs.py` provide admin rights to your AWS account
- Make sure your log file split size, `inputs.py` and InfluxDB account settings are setup as needed (see below)

----

## Quick start deployment via Python [recommended]

Deploy your Lambda function via the steps below (Windows):

1. Double-click `install.bat`
2. Double-click `deploy_aws_lambda.bat` 

Next, test your Lambda function by uploading a log file to your S3 bucket (in the `device_id/session/split.MFX` structure).

Note: You can use `delete_aws_lambda.bat` to remove the Lambda execution role, Lambda function and S3 event triggers. This is useful if you e.g. need to update your function. Once deleted, you can run `deploy_aws_lambda.bat` again to re-deploy.


#### Test the Lambda function 
You can log in to your AWS account, go to `Lambda/Functions/canedge-influxdb-writer` and click `Monitor/Logs` to see all invocations and the resulting output. This lets you verify that your uploaded log files are processed as expected.

----

### Dependencies, log file size and InfluxDB account type
If you're initially testing your setup with a free InfluxDB Cloud starter account, keep in mind that there is a 'write restriction' of 5 MB per 5 minutes. This means that if you try to write e.g. 30 MB of data in one log file, it will take > 30 minutes. This exceeds the AWS Lambda max timeout. If you're using AWS Lambda, we recommend that you ensure your log file split size is 2-5 MB and that the data you extract is optimized (i.e. only push relevant signals at relevant resampled frequency).

For 'production setups', we recommend using a paid InfluxDB Cloud or self-hosting InfluxDB if you wish to use AWS Lambda functions.

----

## Regarding AWS and Lambda costs
We recommend tracking your AWS billing costs when working with Lambda functions to ensure everything is set up correctly. We do not take responsibility for incorrect implementations or unexpected costs related to implementation of the below. Note also that the below is intended as a 'getting started' guide - not a fully cost optimized setup.