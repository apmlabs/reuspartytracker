import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUX_ORG = "reusparty"
INFLUX_BUCKET = "party_data"

def get_client():
    return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def save_party_data(people_count, party_level):
    with get_client() as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("party").field("people_count", people_count).field("party_level", party_level)
        write_api.write(bucket=INFLUX_BUCKET, record=point)

def save_restaurant_data(restaurants):
    with get_client() as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for plaza, items in restaurants.items():
            for r in items:
                if r.get('busyness') is not None:
                    point = Point("restaurant").tag("name", r['name']).tag("plaza", plaza).field("busyness", r['busyness'])
                    write_api.write(bucket=INFLUX_BUCKET, record=point)

def get_party_history(hours=24):
    with get_client() as client:
        query = f'''from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "party")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''
        result = client.query_api().query(query)
        data = []
        for table in result:
            for record in table.records:
                data.append({"timestamp": record.get_time().isoformat(), "people_count": record.values.get("people_count"), "party_level": record.values.get("party_level")})
        return data

def get_restaurant_history(hours=24):
    with get_client() as client:
        query = f'''from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "restaurant")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'''
        result = client.query_api().query(query)
        data = {}
        for table in result:
            for record in table.records:
                plaza = record.values.get("plaza")
                if plaza not in data:
                    data[plaza] = []
                data[plaza].append({"timestamp": record.get_time().isoformat(), "busyness": record.values.get("busyness")})
        return data
