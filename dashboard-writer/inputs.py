from datetime import datetime, timezone

# -----------------------------------------------
# specify your InfluxDB details
influx_bucket = "influx_bucket_name"
token = "influx_token"
influx_url = "influx_endpoint"
org_id = "influx_org_id"

# -----------------------------------------------
# specify devices to process from local/S3. If local files, ensure they are organized as on your SD card
devices = ["LOG/958D2219"]  # for S3 use ["bucket_name/serial_no"]

# -----------------------------------------------
# specify your DBC path and optionally a specific list of signals to include ([]: use all signals)
dbc_path = "CSS-Electronics-SAE-J1939-DEMO.dbc"
signals = []

# optionally modify resampling frequency ("": disable resampling)
res = "1S"

# -----------------------------------------------
# specify your S3 details (if relevant)
use_s3 = False
key = "s3_key"
secret = "s3_secret"
endpoint = "s3_endpoint"
# cert = "path/to/cert.crt"  # if MinIO + TLS, add path to cert and update utils.py/setup_fs_s3 to verify


# toggle whether to update the last execution datetime on each script execution
use_dynamic = False

# set stop date to a point in the future to load all log files after start date
stop = datetime(year=2099, month=1, day=1, tzinfo=timezone.utc)
