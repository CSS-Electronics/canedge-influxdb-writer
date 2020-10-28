import inputs


def write_influx(name, df):
    """Helper function to write data to InfluxDB
    """
    from influxdb_client import InfluxDBClient, Point, WriteOptions
    from influxdb_client.client.write_api import SYNCHRONOUS

    # check if credentials have been added
    if inputs.influx_url == "influx_endpoint":
        print("\nWARNING: Please add your InfluxDB credentials in inputs.py\n")
        return

    # initialize client and write to InfluxDB
    client = InfluxDBClient(url=inputs.influx_url, token=inputs.token, org=inputs.org_id, debug=False)

    # check that InfluxDB bucket is available, then write data to InfluxDB
    try:
        test = client.query_api().query(f'from(bucket:"{inputs.influx_bucket}") |> range(start: -10s)')
    except Exception as err:
        print_influx_error(str(err))
        return

    _write_client = client.write_api(
        write_options=WriteOptions(batch_size=5000, flush_interval=10_000, jitter_interval=2_000, retry_interval=5_000,)
    )

    _write_client.write(
        inputs.influx_bucket, record=df, data_frame_measurement_name=name,
    )

    print(f"- SUCCESS: {len(df.index)} records of {name} written to InfluxDB\n\n")
    _write_client.__del__()
    client.__del__()


def delete_influx(name):
    """Helper function to delete a 'measurement' from InfluxDB
    """
    from influxdb_client import InfluxDBClient, Point, WriteOptions
    from influxdb_client.client.write_api import SYNCHRONOUS

    client = InfluxDBClient(url=inputs.influx_url, token=inputs.token, org=inputs.org_id, debug=False)

    if client.health().status == "pass":
        start = "1970-01-01T00:00:00Z"
        stop = "2099-01-01T00:00:00Z"

        delete_api = client.delete_api()
        delete_api.delete(
            start, stop, f'_measurement="{name}"', bucket=inputs.influx_bucket, org=inputs.org_id,
        )
    else:
        print("\nWARNING: Unable to connect to InfluxDB - please check your credentials\n\n")


def setup_fs_s3():
    """Helper function to setup a remote S3 filesystem connection.
    """
    import s3fs

    fs = s3fs.S3FileSystem(
        key=inputs.key,
        secret=inputs.secret,
        client_kwargs={
            "endpoint_url": inputs.endpoint,
            # "verify": inputs.cert, # uncomment this when using MinIO with TLS enabled
        },
    )

    return fs


def setup_fs():
    """Helper function to setup the file system.
    """
    from pathlib import Path
    import canedge_browser

    base_path = Path(__file__).parent

    fs = canedge_browser.LocalFileSystem(base_path=base_path)

    return fs


def load_last_run():
    """Helper function for loading the date of last run (if not found, set to 7 days ago)
    """
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    # get the root folder path and specify path to the file with datetime
    f_path = Path(__file__).parent / "last_run.txt"

    fmt = "%Y-%m-%d %H:%M:%S"

    try:
        with open(f_path, mode="r") as file:
            file_data = file.read()
    except:
        print(f"Warning: Unable to load file from {f_path}")

    try:
        last_run = datetime.strptime(file_data.replace("\n", ""), fmt)
        print(f"{f_path} found - loading data from {last_run}")
    except:
        last_run = datetime.utcnow() - timedelta(days=7)
        print(f"{f_path} is invalid - loading data from {last_run} (7 days ago)")

    return last_run.replace(tzinfo=timezone.utc)


def set_last_run():
    """Helper function for writing the last run date & time to local file
    """
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    # get the root folder path and specify path to the file with datetime
    f_path = Path(__file__).parent / "last_run.txt"

    fmt = "%Y-%m-%d %H:%M:%S"
    with open(f_path, mode="w") as file:
        file.write(datetime.utcnow().strftime(fmt))


def print_summary(device_id, log_file, df_phys):
    print(
        "\n---------------",
        f"\nDevice: {device_id} | Log file: {log_file.split(device_id)[-1]} [Extracted {len(df_phys)} decoded frames]\nPeriod: {df_phys.index.min()} - {df_phys.index.max()}\n",
    )


def print_influx_error(err):
    warning = "- WARNING: Unable to write data to InfluxDB |"

    if "CERTIFICATE_VERIFY_FAILED" in err:
        print(f"{warning} check your influx_url ({inputs.influx_url})")
    elif "organization name" in err:
        print(f"{warning} check your org_id ({inputs.org_id})")
    elif "unauthorized access" in err:
        print(f"{warning} check your influx_url and token")
    elif "could not find bucket" in err:
        print(f"{warning} check your influx_bucket ({inputs.influx_bucket})")
    else:
        print(err)
