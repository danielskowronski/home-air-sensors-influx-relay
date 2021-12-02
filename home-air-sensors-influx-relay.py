#!python3
import sys

import tinytuya
import yaml
from influxdb import InfluxDBClient

_cfg = None


def storeMeasurementsToInfluxDB(device, readings):
    try:
        client = InfluxDBClient(
            _cfg["influx"]["host"],
            _cfg["influx"]["port"],
            _cfg["influx"]["user"],
            _cfg["influx"]["pass"],
            _cfg["influx"]["db"],
        )
        print(
            "Sending data to InfluxDB: %s:%s/%s"
            % (_cfg["influx"]["host"], _cfg["influx"]["port"], device["measurement"])
        )
        status = client.write_points(
            [
                {
                    "measurement": device["measurement"],
                    "fields": {
                        "temperature_celsius": readings["temperature_celsius"],
                        "humidity_perc": readings["humidity_perc"],
                        "co2_ppm": readings["co2_ppm"],
                        "voc_ppm": readings["voc_ppm"],
                        "formaldehyde_ppm": readings["formaldehyde_ppm"],
                    },
                }
            ]
        )
        print("Response from InfluxDB: %s" % (status))
    except Exception as e:
        print(e)


def fetchLastMeasurement(device):
    d = tinytuya.OutletDevice(device["id"], device["ip"], device["key"])
    d.set_version(3.3)
    data = d.status()

    readings = {}
    try:
        readings["temperature_celsius"] = float(data["dps"]["18"]) / 10
        readings["humidity_perc"] = float(data["dps"]["19"]) / 10
        readings["co2_ppm"] = float(data["dps"]["22"]) / 1
        readings["voc_ppm"] = float(data["dps"]["21"]) / 10
        readings["formaldehyde_ppm"] = float(data["dps"]["2"]) / 100
        print(readings)
    except Exception as e:
        print(e)

    return readings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("provide config.yml as CLI param")
        sys.exit(1)
    stream = open(sys.argv[1], "r")
    loadedFile = yaml.load(stream, Loader=yaml.SafeLoader)
    _cfg = loadedFile

    for device in _cfg["tuya"]:
        storeMeasurementsToInfluxDB(device, fetchLastMeasurement(device))
