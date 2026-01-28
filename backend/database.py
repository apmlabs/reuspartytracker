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

def save_party_data(people_count, party_level, car_count=0, police_score=0, police_cars=0, police_vans=0, police_uniformed=0):
    with get_client() as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point("party").field("people_count", people_count).field("party_level", party_level).field("car_count", car_count).field("police_score", police_score).field("police_cars", police_cars).field("police_vans", police_vans).field("police_uniformed", police_uniformed)
        write_api.write(bucket=INFLUX_BUCKET, record=point)

def save_restaurant_data(restaurants):
    with get_client() as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for plaza, items in restaurants.items():
            for r in items:
                # Closed = 0, Open + busyness = actual, Open + no busyness = skip
                if not r.get('is_open'):
                    busyness = 0
                elif r.get('busyness') is not None:
                    busyness = r.get('busyness')
                else:
                    continue  # Open but no data - exclude
                point = Point("restaurant").tag("name", r['name']).tag("plaza", plaza).field("busyness", busyness)
                write_api.write(bucket=INFLUX_BUCKET, record=point)

def get_party_history(hours=24):
    with get_client() as client:
        query = f'''from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "party")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            |> sort(columns: ["_time"])'''
        result = client.query_api().query(query)
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "timestamp": record.get_time().isoformat(),
                    "people_count": record.values.get("people_count"),
                    "party_level": record.values.get("party_level"),
                    "car_count": record.values.get("car_count") or 0,
                    "police_score": record.values.get("police_score") or 0,
                    "police_cars": record.values.get("police_cars") or 0,
                    "police_vans": record.values.get("police_vans") or 0,
                    "police_uniformed": record.values.get("police_uniformed") or 0
                })
        data.sort(key=lambda x: x['timestamp'])
        return data

def get_restaurant_history(hours=24):
    with get_client() as client:
        # Aggregate by plaza and time window, compute mean busyness
        query = f'''from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "restaurant")
            |> filter(fn: (r) => r._field == "busyness")
            |> group(columns: ["plaza"])
            |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)'''
        result = client.query_api().query(query)
        data = {}
        for table in result:
            for record in table.records:
                plaza = record.values.get("plaza")
                if plaza not in data:
                    data[plaza] = []
                data[plaza].append({"timestamp": record.get_time().isoformat(), "busyness": round(record.get_value() or 0)})
        # Sort by timestamp
        for plaza in data:
            data[plaza].sort(key=lambda x: x['timestamp'])
        return data

def save_top_restaurant_data(restaurants):
    with get_client() as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for r in restaurants:
            if not r.get('is_open'):
                busyness = 0
            elif r.get('busyness') is not None:
                busyness = r.get('busyness')
            else:
                continue
            point = Point("top_restaurant").tag("name", r['name']).field("busyness", busyness)
            write_api.write(bucket=INFLUX_BUCKET, record=point)

def get_top_restaurant_history(hours=24):
    with get_client() as client:
        query = f'''from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -{hours}h)
            |> filter(fn: (r) => r._measurement == "top_restaurant")
            |> filter(fn: (r) => r._field == "busyness")
            |> group(columns: ["name"])
            |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)'''
        result = client.query_api().query(query)
        data = {}
        for table in result:
            for record in table.records:
                name = record.values.get("name")
                if name not in data:
                    data[name] = []
                data[name].append({"timestamp": record.get_time().isoformat(), "busyness": round(record.get_value() or 0)})
        for name in data:
            data[name].sort(key=lambda x: x['timestamp'])
        return data
