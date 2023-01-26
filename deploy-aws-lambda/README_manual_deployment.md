# Manual deployment [not recommended]

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
