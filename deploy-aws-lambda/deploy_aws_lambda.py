import os
import json
import boto3
import shutil
import tempfile
import datetime
import sys
import time

from pathlib import Path
parent = Path(__file__).resolve().parent.parent
sys.path.append(str(parent))
import inputs as inp

# Switch to working directory of the bat file
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# define initial variables
AWS_ACCESS_KEY = inp.key
AWS_SECRET_KEY = inp.secret

try:
    REGION = inp.endpoint.split(".")[1]
except:
    print(f"Unable to extract region from {inp.endpoint} - check if correct syntax is used ala http://s3.region.amazonaws.com")
    print("Exiting script")
    sys.exit()
    
S3_BUCKET = inp.devices[0].split("/")[0]
LAMBDA_ROLE_NAME = "canedge-influxdb-lambda-role"
LAMBDA_FUNCTION_NAME = "canedge-influxdb-writer"

PYTHON_BUILD = "python3.9"
LAMBDA_HANDLER = "lambda_function.lambda_handler"
LAMBDA_ZIP_FILE = "lambda_function"
files_to_archive = ["lambda_function.py", "../inputs.py", "../utils.py","../utils_db.py", "../dbc_files"]
ARN_LAYER_CSV = "arn-layers/lambda_layer_arns.csv"


print("This script will deploy an AWS Lambda function in your AWS account.")
print(
    "It will also add S3 triggers for MF4/MFC/MFE/MFM files and the relevant roles/permissions."
)
print(
    "- Ensure that you've updated inputs.py with your details and tested this locally"
)
print("- Ensure that the S3 credentials in your inputs.py have admin permissions")
print(
    "- If you have previously deployed a Lambda function, use the deletion script to remove it"
)

# Configure boto3 client
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=REGION
)

# Get AWS S3 bucket region
s3 = session.client("s3")

try:
    response = s3.get_bucket_location(Bucket=S3_BUCKET)
    REGION_BUCKET = response["LocationConstraint"]
except Exception as e:
    print("\n")
    print(e)
    print("\nUnable to establish S3 connection.")
    print("- Please check if your S3 credentials in inputs.py are correct and provide administrative rights")
    print("- Please check if the 1st entry in your 'devices' list correctly includes your S3 bucket name")
    print("- Exiting script")
    sys.exit()
    
if REGION_BUCKET != REGION:
    print(f"WARNING: Bucket region is {REGION_BUCKET} and differs from session region {REGION} - please review.")
    print("- Exiting script")

    sys.exit()
    


# Get AWS account ID
sts = session.client("sts")
response = sts.get_caller_identity()
AWS_ACCOUNT_ID = response["Account"]

print(
    f"--------------\nConfigured AWS boto3 client and account ID {AWS_ACCOUNT_ID}"
)

temp_dir = tempfile.mkdtemp()

for f in files_to_archive[:-1]:
    shutil.copy2(f, temp_dir)

shutil.copytree(
    files_to_archive[-1], f"{temp_dir}/{os.path.basename(files_to_archive[-1])}"
)

shutil.make_archive(LAMBDA_ZIP_FILE, "zip", root_dir=temp_dir)

print(f"--------------\nZipped relevant files into {LAMBDA_ZIP_FILE}.zip")

# Look up the relevant pre-built Lambda ARN layer from the CSV lambda_layer_arns.csv based on region
with open(ARN_LAYER_CSV, "r") as f:
    lines = f.readlines()
    for line in lines:
        if REGION in line:
            LAMBDA_ARN_LAYER = line.split(",")[1].replace("\n", "")

print(f"--------------\nUsed {REGION} to lookup Lambda ARN layer {LAMBDA_ARN_LAYER}")

# Create the lambda role if it does not already exist
LAMBDA_ROLE_ARN = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{LAMBDA_ROLE_NAME}"

iam = session.client("iam")
trust_policy = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
)


try:
    role = iam.get_role(RoleName=LAMBDA_ROLE_NAME)
    print(f"--------------\nIAM role {LAMBDA_ROLE_NAME} already exists")
except iam.exceptions.NoSuchEntityException:
    # with open("trust_policy.json", "r") as f:
    #     trust_policy = f.read()
    iam.create_role(RoleName=LAMBDA_ROLE_NAME, AssumeRolePolicyDocument=trust_policy)
    print(
        f"--------------\nCreated new AWS lambda role {LAMBDA_ROLE_NAME} with ARN {LAMBDA_ROLE_ARN}"
    )    
    print("Waiting 10 seconds ...")
    time.sleep(10)
    iam.attach_role_policy(
        RoleName=LAMBDA_ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )
    print(
        f"--------------\nAttached role policy AWSLambdaBasicExecutionRole"
    )
    print("Waiting 10 seconds ...")
    time.sleep(10)
    iam.attach_role_policy(
        RoleName=LAMBDA_ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
    )
    print(
        f"--------------\nAttached role policy AmazonS3FullAccess"
    )
    print("Waiting 20 seconds ...")
    time.sleep(20)

# Create the lambda function if it does not already exist
lambda_client = session.client("lambda")
try:
    lambda_client.create_function(
        FunctionName=LAMBDA_FUNCTION_NAME,
        Runtime=PYTHON_BUILD,
        Role=LAMBDA_ROLE_ARN,
        Handler=LAMBDA_HANDLER,
        Code={"ZipFile": open(f"{LAMBDA_ZIP_FILE}.zip", "rb").read()},
        Timeout=180,
        MemorySize=1024,
        Layers=[LAMBDA_ARN_LAYER],
    )
    print(
        f"--------------\nDeployed the AWS Lambda function {LAMBDA_FUNCTION_NAME} in region {REGION}"
    )
    print("Waiting 10 seconds ...")
    time.sleep(10)
except Exception as e:
    print("--------------\nUnable to create lambda function")
    print(e)


# Create unique statement ID via timestamp and add S3 permission to trigger Lambda
dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
statement_id = f"canedges3event{dt}"

try:
    lambda_client.add_permission(
        FunctionName=LAMBDA_FUNCTION_NAME,
        StatementId=statement_id,
        Action="lambda:InvokeFunction",
        Principal="s3.amazonaws.com",
        SourceArn=f"arn:aws:s3:::{S3_BUCKET}",
        SourceAccount=AWS_ACCOUNT_ID,
    )
    print(
        f"--------------\nAdded S3 InvokeFunction permissions for the Lambda execution role using the statement ID {statement_id}"
    )
    print("Waiting 10 seconds ...")
    time.sleep(10)
except Exception as e:
    print(
        f"--------------\nWARNING: Failed to add S3 InvokeFunction permissions for the Lambda execution role using the statement ID {statement_id}"
    )
    print(e)

# Add S3 event triggers for MF4/MFC/MFE/MFM suffixes
notification_config = dict(
    {
        "LambdaFunctionConfigurations": [
            {
                "Id": "MF4_TRIGGER",
                "LambdaFunctionArn": f"arn:aws:lambda:{REGION}:{AWS_ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {"FilterRules": [{"Name": "suffix", "Value": ".MF4"}]}
                },
            },
            {
                "Id": "MFC_TRIGGER",
                "LambdaFunctionArn": f"arn:aws:lambda:{REGION}:{AWS_ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {"FilterRules": [{"Name": "suffix", "Value": ".MFC"}]}
                },
            },
            {
                "Id": "MFE_TRIGGER",
                "LambdaFunctionArn": f"arn:aws:lambda:{REGION}:{AWS_ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {"FilterRules": [{"Name": "suffix", "Value": ".MFE"}]}
                },
            },
            {
                "Id": "MFM_TRIGGER",
                "LambdaFunctionArn": f"arn:aws:lambda:{REGION}:{AWS_ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {"FilterRules": [{"Name": "suffix", "Value": ".MFM"}]}
                },
            },
        ]
    }
)


try:
    s3.put_bucket_notification_configuration(
        Bucket=S3_BUCKET, NotificationConfiguration=notification_config
    )
    print(f"--------------\nAdded the S3 bucket {S3_BUCKET} as trigger source")
except Exception as e:
    print(e)

# clean up
if os.path.exists(f"{LAMBDA_ZIP_FILE}.zip"):
    os.remove(f"{LAMBDA_ZIP_FILE}.zip")
    print(f"--------------\nClean up: {LAMBDA_ZIP_FILE}.zip has been deleted.")
else:
    print(f"--------------\nClean up: {LAMBDA_ZIP_FILE}.zip was not deleted as it does not exist.")

print(f"--------------\nComplete: Test your Lambda function by uploading a log file to S3.")
