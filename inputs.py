# -----------------------------------------------
# specify your InfluxDB details
influx_bucket = "influx_bucket_name"
token = "influx_token"
influx_url = "influx_endpoint"
org_id = "influx_org_id"

# -----------------------------------------------
# specify devices to process from local disk via ["folder/device_id"] or S3 via ["bucket/device_id"]
devices = ["LOG/2F6913DB"]

# -----------------------------------------------
# specify DBC paths and a list of signals to process ([]: include all signals)
# optionally include signal prefixes to make CAN ID, PGN and/or BusChannel explicit
dbc_paths = ["dbc_files/canmod-gps.dbc"]
signals = []
can_id_prefix = False
pgn_prefix = False
bus_prefix = False

# specify resampling frequency. Setting this to "" means no resampling (much slower)
res = "5S"

# -----------------------------------------------
# specify whether to load data from S3 (and add server details if relevant)
s3 = False
key = "s3_key"
secret = "s3_secret"
endpoint = "s3_endpoint"  # e.g. http://s3.us-east-1.amazonaws.com or http://192.168.0.1:9000
region = "s3_region" # only relevant if you are using more recent builds of MinIO S3 as the backend
# cert = "path/to/cert.crt"  # if MinIO + TLS, add path to cert and update utils.py/setup_fs to verify

# -----------------------------------------------
# if dynamic = True, data is loaded dynamically based on most recent data in InfluxDB - else default_start is used
dynamic = True
default_start = "2022-01-01 00:00:00"
days_offset = 1  # offsets data to start at 'today - days_offset'. Set to None to use original timestamps

# if you're using data encryption, you can add the password below
pw = {"default": "password"}

# if you need to process multi-frame data, set tp_type to "uds", "j1939" or "nmea"
tp_type = ""
