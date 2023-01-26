import s3fs
from utils import load_dbc_files, ProcessData, MultiFrameDecoder, restructure_data
from utils_db import SetupInflux
import inputs as inp


def lambda_handler(event, context=None):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    log_files = [bucket + "/" + key]

    fs = s3fs.S3FileSystem(anon=False)
    db_list = load_dbc_files(inp.dbc_paths)

    # initialize connection to InfluxDB
    influx = SetupInflux(inp.influx_url, inp.token, inp.org_id, inp.influx_bucket, inp.res)

    # process the log files and write extracted signals to InfluxDB
    proc = ProcessData(fs, db_list, inp.signals, inp.days_offset)

    for log_file in log_files:
        df_raw, device_id = proc.get_raw_data(log_file, inp.pw)

        if inp.tp_type != "":
            tp = MultiFrameDecoder(inp.tp_type)
            df_raw = tp.combine_tp_frames(df_raw)

        df_phys = proc.extract_phys(df_raw)
        proc.print_log_summary(device_id, log_file, df_phys)

        df_phys = restructure_data(df_phys,inp.res)

        influx.write_signals(device_id, df_phys)
