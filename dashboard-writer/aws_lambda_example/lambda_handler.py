import s3fs
from utils import setup_fs, load_dbc_files, list_log_files, SetupInflux, DataWriter
import inputs


def lambda_handler(event, context=None):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    log_files = [bucket + "/" + key]

    fs = s3fs.S3FileSystem(anon=False)
    db_list = load_dbc_files(inputs.dbc_paths)

    # initialize connection to InfluxDB
    influx = SetupInflux(
        influx_url=inputs.influx_url, token=inputs.token, org_id=inputs.org_id, influx_bucket=inputs.influx_bucket
    )

    # process the log files and write extracted signals to InfluxDB
    writer = DataWriter(fs=fs, db_list=db_list, signals=inputs.signals, res=inputs.res, db_func=influx.write_influx)
    writer.decode_log_files(log_files)
