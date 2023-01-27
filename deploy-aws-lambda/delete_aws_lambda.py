import os
import boto3
import sys 
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

print(
    "This batch script will remove the Lambda function, the Lambda execution role and S3 bucket triggers."
)
print(
    "- Ensure that you have added your admin AWS S3 credentials and details to the inputs.py"
)
print(
    "- Double check that the removal was done as expected by reviewing your AWS account"
)
print(
    "- We do not take any responsibility for issues involved in the use of this script"
)

# Configure boto3 client
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=REGION
)

# Get AWS S3 bucket region
s3 = session.client("s3")

try:
    response = s3.get_bucket_location(Bucket=S3_BUCKET)
    REGION = response["LocationConstraint"]
except Exception as e:
    print("\n")
    print(e)
    print("\nUnable to establish S3 connection.")
    print("- Please check if your S3 credentials in inputs.py are correct and provide administrative rights")
    print("- Please check if the 1st entry in your 'devices' list correctly includes your S3 bucket name")
    print("- Exiting script")
    sys.exit()



# Get AWS account ID
sts = session.client("sts")
response = sts.get_caller_identity()
AWS_ACCOUNT_ID = response["Account"]

print(
    f"--------------\nConfigured AWS boto3 client and extracted S3 bucket region {REGION} and account ID {AWS_ACCOUNT_ID}"
)

# delete the lambda role if it exists
LAMBDA_ROLE_ARN = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{LAMBDA_ROLE_NAME}"

iam = session.client("iam")

try:
    iam.detach_role_policy(
        RoleName=LAMBDA_ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )
    iam.detach_role_policy(
        RoleName=LAMBDA_ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
    )
    iam.delete_role(RoleName=LAMBDA_ROLE_NAME)
    print(f"--------------\nIAM role {LAMBDA_ROLE_NAME} deleted")
except iam.exceptions.NoSuchEntityException:
    print(f"--------------\nIAM role {LAMBDA_ROLE_NAME} does not exist")


# Delete the lambda function if it exist
lambda_client = session.client("lambda")
try:
    lambda_client.delete_function(FunctionName=LAMBDA_FUNCTION_NAME)
    print(
        f"--------------\nDeleted the AWS Lambda function {LAMBDA_FUNCTION_NAME} in region {REGION}"
    )
except Exception as e:
    print("--------------\nUnable to delete lambda function")
    print(e)

# Delete the S3 triggers by writing blank notification config
notification_config = dict({})

try:
    s3.put_bucket_notification_configuration(
        Bucket=S3_BUCKET, NotificationConfiguration=notification_config
    )
    print(f"--------------\nRemoved all event triggers from S3 bucket {S3_BUCKET}")
except Exception as e:
    print(e)

print("\nDeletion completed.")