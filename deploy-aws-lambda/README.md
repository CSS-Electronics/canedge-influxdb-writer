# AWS Lambda Automation

AWS Lambda functions are a smart way to auto-execute code on every log file upload.

Below we describe how you can set up an AWS Lambda function to automatically run the script when a new log file is uploaded.

----

## Before you deploy

This is an advanced topic and we recommend that you get the basics in place first:
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

Note: You can use `delete_aws_lambda.bat` to remove the Lambda execution role, Lambda function and S3 event triggers. This is useful if you e.g. need to update your function.

----

### Dependencies, log file size and InfluxDB account type
The canedge-influxdb-writer script relies on a number of dependencies that need to be provided to the AWS Lambda function. To make this easy, we have pre-built 'layers' for the major AWS S3 regions. You can find the latest layer list in our Releases page. See below for details. By providing your AWS Lambda function with an 'ARN identifier' for a pre-built layer, you ensure that all relevant dependencies are in place. The ARN should match the region that your S3 bucket is setup in.

If you're initially testing your setup with a free InfluxDB Cloud starter account, keep in mind that there is a 'write restriction' of 5 MB per 5 minutes. This means that if you try to write e.g. 30 MB of data, it will take > 30 minutes. This exceeds the AWS Lambda max timeout. If you're using AWS Lambda, we recommend that you ensure your log file split size is 2-5 MB and that the data you extract is optimized (i.e. only push relevant signals at relevant resampled frequency). Depending on your use case, this will let you set up a basic PoC.

For 'production setups', we recommend using a paid InfluxDB Cloud or self-hosting InfluxDB if you wish to use AWS Lambda functions.

---

## Manual deployment [not recommended]

Below steps can be taken to manually deploy your lambda function via the AWS GUI. However, we strongly recommend the above batch script method to ensure correct installation.

1. Create an [IAM execution](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html) role (not user) with permissions: `AWSLambdaBasicExecutionRole` + `AmazonS3FullAccess` 
2. Go to 'Services/Lambda', then select your S3 bucket region (upper right corner)
3. Add a new Lambda function with a name, a Python 3.7 environment and your new execution role
4. Add a 'Trigger': Select S3, your test bucket, `All object create events` and suffix `.MF4`
5. Create a zip with `lambda_function.py`, `utils.py`, `utils_db.py`, `inputs.py` and your `*.dbc` (ensure your inputs are updated)
6. Upload the zip via the Lambda 'Actions' button and confirm that your code shows in the online code editor
7. Find the pre-built layer ARN for your AWS S3 region in the `lambda_layer_arns.csv` file
8. In the 'Layers' section, click 'Add a layer/Specify an ARN' and parse the ARN matching your region
9. Go to 'Configuration/General configuration' and set the 'Timeout' to `3 min` and memory to `1024 MB` (you can tweak these later)
10. Save the script and click 'Deploy' (important), then 'Test' (using the below test data) and verify that it succeeds
11. Click 'Test' in the upper right corner
12. Add the test event JSON content below (update to match details of an actual MF4 test file on S3)
13. When you're ready, click 'Actions/Publish' to save a new version
14. In AWS Services, go to Cloudwatch/Logs/Log groups and click your Lambda function to monitor events
15. Download a logfile via CANcloud from your main bucket and upload to your test bucket via CANcloud (from the Home tab)
16. Verify that the Lambda function is triggered within a minute and check from the log output that it processes the data
17. Verify that data is written correctly to InfluxDB

#### Lambda function test event data

```
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "your-source-bucket-name",
          "arn": "arn:aws:s3:::your-source-bucket-name"
        },
        "object": {
          "key": "<device_id>/<test_file_session_id>/<full_test_file_name.MF4>"
        }
      }
    }
  ]
}
```


---

## Regarding AWS and Lambda costs
We recommend tracking your AWS billing costs when working with Lambda functions to ensure everything is set up correctly. We do not take responsibility for incorrect implementations or unexpected costs related to implementation of the below. Note also that the below is intended as a 'getting started' guide - not a fully cost optimized setup.