# requires Docker to be running

import os, json, sys
import subprocess

# specify base details and region list
layer_name = "css-canedge-influxdb-writer"
layer_description = "CSS Electronics canedge-influxdb-writer script dependencies for use in AWS Lambda functions"
csv_path = "canedge-influxdb-writer/aws_lambda_example/lambda_layer_arns.csv"
run_req_build = True

regions = [
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "eu-central-1",
    "eu-north-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]

# create zip with requirements.txt dependencies
if run_req_build:
    os.system("rmdir /S/Q python")
    os.system("mkdir python\lib\python3.7\site-packages")
    os.system(
        'docker run -v "%cd%":/var/task "lambci/lambda:build-python3.7" /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.7/site-packages/; exit"'
    )
    os.system("rmdir /S/Q python\\lib\\python3.7\\site-packages\\botocore")
    os.system("zip -r canedge-influxdb-writer.zip python")

# for each region, publish AWS layer with build zip
region_arn_list = []

print("we get here")

for region in regions:
    print(f"executing region {region}")

    # create the layers
    arn_output = subprocess.check_output(
        f'aws lambda publish-layer-version --region {region} --layer-name {layer_name} --description "{layer_description}" --cli-connect-timeout 6000 --license-info "MIT" --zip-file "fileb://canedge-influxdb-writer.zip" --compatible-runtimes python3.7',
        shell=True,
    ).decode("utf-8")

    print("We build the layer", arn_output)

    version = int(json.loads(arn_output)["Version"])

    # make them public
    make_public = subprocess.check_output(
        f"aws lambda add-layer-version-permission --layer-name {layer_name} --version-number {version} --statement-id allAccountsExample --principal * --action lambda:GetLayerVersion --region {region}",
        shell=True,
    )

    print("Build layer:", arn_output)

    print("Make public:", make_public)

    arn = str(json.loads(arn_output)["LayerVersionArn"])
    region_arn = f"{region},{arn}\n"
    region_arn_list.append(region_arn)

# write data to CSV
output_file = open(csv_path, "w")
for region_arn in region_arn_list:
    output_file.write(region_arn)

output_file.close()

print(f"Completed writing {len(region_arn_list)} out of {len(regions)} to CSV {csv_path}")
