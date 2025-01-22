import json
import paho.mqtt.client as mqtt

from area_tank import Tank
from distribution_pipeline import Pipeline

class Area:
    def __init__(self, area_data: dict):
        self.name = area_data['name']
        self.area_tanks = self.create_tank_and_pipeline_sensors(area_data['tanks'])

    def create_tank_and_pipeline_sensors(self, tanks_data):
        area_tanks_sensors = []
        pipeline_sensors = {}

        for tank in tanks_data:
            tank_name = f"{self.name}/{tank['name']}"
            area_tanks_sensors.append(
                Tank(
                    name=tank_name,
                    longitude=tank['longitude'],
                    latitude=tank['latitude']
                )
            )

            tank_pipelines = []
            for tank_pipeline in tank['pipelines']:
                pipeline_name = f"{tank_name}/{tank_pipeline['name']}"
                tank_pipelines.append(
                    Pipeline(
                        name=pipeline_name,
                        longitude=tank_pipeline['longitude'],
                        latitude=tank_pipeline['latitude']
                    )
                )
            pipeline_sensors[tank_name] = tank_pipelines

        self.pipeline_sensors = pipeline_sensors
        return area_tanks_sensors

    def generate_data(self, client, base_topic):
        """Generate and publish sensor data for all tanks and pipelines in the area."""
        for tank in self.area_tanks:
            # Generate tank data
            tank_data = tank.generate_data()
            tank_data.update({"area": self.name, "type": "tank", "name": tank.name})
            
            # Publish tank data
            tank_topic = f"{base_topic}/{tank.name}"
            client.publish(tank_topic, json.dumps(tank_data))
            print(f"Published to {tank_topic}: {tank_data}")

            # Extract only PH and Salinity for pipelines
            regulated_tank_data = {"PH": tank_data["PH"], "Salinity": tank_data["Salinity"]}
            pipelines = self.pipeline_sensors.get(tank.name, [])
            
            # Generate and publish pipeline data
            for pipeline in pipelines:
                pipeline_data = pipeline.generate_data(regulated_tank_data)
                pipeline_data.update({"area": self.name, "type": "pipeline", "name": pipeline.name})
                
                pipeline_topic = f"{base_topic}/{pipeline.name}"
                client.publish(pipeline_topic, json.dumps(pipeline_data))
                print(f"Published to {pipeline_topic}: {pipeline_data}")

