# AWS Lambda Automation

AWS Lambda functions are a smart way to auto-execute code on every log file upload.

Below we describe how you can set up an AWS Lambda function to automatically run the script when a new log file is uploaded.

---

## Before you get started

This is an advanced topic and we recommend that you get the basics in place first:
- Test that your InfluxDB/Grafana setup works with the sample data
- Test that your setup works with your own data/server when manually running the script from your PC
- Make sure your log file split size, `inputs.py` and InfluxDB account settings are setup as needed (see below)
- Create a test bucket in the same region as your main bucket and use this for the initial setup

### Regarding dependencies
The canedge-influxdb-writer script relies on a number of dependencies that need to be provided to the AWS Lambda function. To make this easy, we have pre-built 'layers' for the major AWS S3 regions. You can find the latest layer list in our Releases page. See below for details. By providing your AWS Lambda function with an 'ARN identifier' for a pre-built layer, you ensure that all relevant dependencies are in place. The ARN should match the region that your S3 bucket is setup in.

### Regarding log file size and InfluxDB account type
If you're initially testing your setup with a free InfluxDB Cloud starter account, keep in mind that there is a 'write restriction' of 5 MB per 5 minutes. This means that if you try to write e.g. 30 MB of data, it will take > 30 minutes. This exceeds the AWS Lambda max timeout. If you're using AWS Lambda, we recommend that you ensure your log file split size is 2-5 MB and that the data you extract is optimized (i.e. only push relevant signals at relevant resampled frequency). Depending on your use case, this will let you set up a basic PoC.

For 'production setups', we recommend self-hosting InfluxDB or using a paid InfluxDB Cloud if you wish to use AWS Lambda function.

---

## Deploy your AWS Lambda function

1. Create an [IAM execution](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html) role with permissions: `AWSLambdaBasicExecutionRole` + `AmazonS3FullAccess` 
2. Go to 'Services/Lambda', then select your S3 bucket region (upper right corner)
3. Add a new Lambda function with a name, a Python 3.7 environment and your execution role
4. Add a 'Trigger': Select S3, your test bucket, `All object create events` and suffix `.MF4`
5. Create a zip with `lambda_function.py`, `utils.py`, `utils_db.py`, `inputs.py` and your `*.dbc` (ensure your inputs are updated)
6. Upload the zip via the Lambda 'Actions' button and confirm that your code shows in the online code editor
7. Find the pre-built layer ARN for your AWS S3 region in the `lambda_layer_arns.csv` file
8. In the 'Designer' tap, click Layers/Add a layer/Specify an ARN and parse your ARN
9. Scroll to 'Basic settings' and set the 'Timeout' to `3 min` and memory to `1024 MB` (you can test/tweak these later)
10. Save the script and click 'Deploy', then 'Test' (using the below test data) and verify that it succeeds
11. Click 'Test' in the upper right corner and add the test JSON content below
12. When you're ready, click 'Actions/Publish' to save a new version
13. In AWS Services, go to Cloudwatch/Logs/Log groups and click your Lambda function to monitor events
14. Download a logfile via CANcloud from your main bucket and upload to your test bucket via CANcloud (from the Home tab)
15. Verify that the Lambda function is triggered within a minute and check from the log output that it processes the data
16. Verify that data is written correctly to InfluxDB

Once tested, change the 'Trigger' S3 bucket to your main bucket and verify that it works as intended over a period.


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


#### Troubleshooting

Typical issues that may arise include the following:
1. If you do not create your IAM execution role with the correct policies, you'll get errors regarding forbidden access
2. It's important that you zip the files outlined directly, rather than putting them in a folder and zipping the folder 
3. Make sure to update the timeout - the script won't be able to run with the default 3 second timeout 


<!--
---

## Build custom ARN layer package
If you need to create your own AWS Lambda layer, you can take outset in the steps below (Windows):

1. Add a new build folder for the build process, e.g. `aws-lambda-layer/`
2. Install [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
3. Open your command prompt and run `docker pull lambci/lambda`
4. Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
5. Open your command prompt and run `aws configure` and provide your credentials
6. Open Docker and go to 'Settings/Resources/File Sharing', then add your new folder
7. Copy the canedge-influxdb-writer `requirements.txt` file into your build folder
8. In the build folder, create a `build.bat` file with below content (update the layer name and region)
9. Open your command line in the folder and run `build.bat` - this will take a few minutes
10. Once done, you can use the `LayerVersionArn` value from the `APN.txt` - e.g. as below:  
`arn:aws:lambda:us-east-2:319723967016:layer:css-electronics-canedge-influxdb-writer:10`

```
rmdir /S/Q python
mkdir python\lib\python3.7\site-packages
docker run -v "%cd%":/var/task "lambci/lambda:build-python3.7" /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.7/site-packages/; exit"
rmdir /S/Q python\lib\python3.7\site-packages\botocore
zip -r canedge-influxdb-writer.zip python
aws lambda publish-layer-version --region us-east-2 --layer-name my-layer --description "canedge-influxdb-writer Script Dependencies" --zip-file "fileb://canedge-influxdb-writer.zip" --compatible-runtimes python3.7 > APN.txt
```

## Build multiple regions 
1. Copy the file `build_layers.py` to the root of the repo 
2. Run the file via `python build_layers.py` 
3. If you've already built the zip file with dependencies, you can set this step to False in the code 

-->

---

## Regarding AWS and Lambda costs
We recommend tracking your AWS billing costs when working with Lambda functions to ensure everything is set up correctly. We do not take responsibility for incorrect implementations or unexpected costs related to implementation of the below. Note also that the below is intended as a 'getting started' guide - not a fully cost optimized setup.