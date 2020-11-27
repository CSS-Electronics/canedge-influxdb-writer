# -----------------------------------------------
# specify your InfluxDB details
influx_bucket = "influx_bucket_name"
token = "influx_token"
influx_url = "influx_endpoint"
org_id = "influx_org_id"

# -----------------------------------------------
# specify devices to process (from a local folder or S3 bucket)
# If local, ensure logs are organized correctly: folder/device_id/session/split.MF4
# Syntax: Local: ["folder/device_id"] | S3: ["bucket/device_id"]
devices = ["LOG/958D2219"]


# -----------------------------------------------
# specify DBC paths and a list of signals to process ([]: include all signals)
dbc_paths = ["CSS-Electronics-SAE-J1939-DEMO.dbc"]
signals = []

# specify resampling frequency ("": no resampling)
res = "1S"

# -----------------------------------------------
# specify whether to load data from S3 (and add server details if relevant)
s3 = False
key = "s3_key"
secret = "s3_secret"
endpoint = "s3_endpoint"  # e.g. http://s3.us-east-1.amazonaws.com or http://192.168.0.1:9000
# cert = "path/to/cert.crt"  # if MinIO + TLS, add path to cert and update utils.py/setup_fs to verify

# -----------------------------------------------
# if dynamic = True, data from S3 is loaded dynamically based on the last data found in InfluxDB
# if dynamic = False (or no data is found in InfluxDB for a device), the default_start date is used
dynamic = True
default_start = "2020-01-01 00:00:00"
