import os
import time
import json
import argparse
from enum import Enum
from distribution_area import Area

import paho.mqtt.client as mqtt

# MQTT Broker Configuration
#BROKER = "localhost"  # Replace with your broker's IP if not local

BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = 1883
BASE_TOPIC = "water_quality"

def initiate_distribution_network(file_path):
    """
    Reads a JSON configuration file and returns the parsed data.
    :param file_path: Path to the JSON file.
    :return: List of Area objects.
    """
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        areas = []
        for area_config in config['areas']:
            areas.append(Area(area_data=area_config))
        return areas
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

# MQTT Publishing
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

def main():
    parser = argparse.ArgumentParser(description="Run the water quality simulation.")
    parser.add_argument("--config_file", type=str, required=True, help="Path to the configuration JSON file.")
    args = parser.parse_args()

    config_file = args.config_file    
    areas = initiate_distribution_network(config_file)

    if not areas:
        print("No areas to simulate. Exiting.")
        return

    try:
        while True:
            for area in areas:
                area.generate_data(client, BASE_TOPIC)
                time.sleep(10)  # Simulate reporting interval
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        client.disconnect()



if __name__ == "__main__":
    main()
