import random
import time

class Pipeline:
    class RateGroup:
        LOW = (3, 5)  # Feet per second
        MEDIUM = (6, 8)  # Feet per second
        HIGH = (9, 10)  # Feet per second

    def __init__(self, name, longitude, latitude):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.sensors = {
            "PH": (6, 8.5),
            "Salinity": (0, 600),
            "Flow": Pipeline.RateGroup.MEDIUM
        }
        

    def generate_data(self, tank_data):
        """Generate random sensor data for the pipeline."""
        # Simulate flow rate based on pipe size
        flow_range = self.sensors["Flow"]
        flow_rate = round(random.uniform(*flow_range), 2)

        # Adjust PH and Salinity differences based on flow rate
        if flow_rate >= Pipeline.RateGroup.HIGH[0]:
            ph_difference = random.uniform(0.0, 0.1)
            salinity_difference = random.uniform(-5, 5)
        elif flow_rate <= Pipeline.RateGroup.LOW[1]:
            ph_difference = random.uniform(0.5, 1.2)  # Larger increase for low flow
            salinity_difference = random.uniform(20, 30)  # Larger increase for low flow
        else:
            ph_difference = random.uniform(0.1, 0.5)
            salinity_difference = random.uniform(0, 25)

        # Use tank PH and Salinity values adjusted by differences
        data = {
            "PH": round(tank_data["PH"] + ph_difference, 2),
            "Salinity": round(tank_data["Salinity"] + salinity_difference, 2),
            "Flow": flow_rate
        }
        data['longitude'] = self.longitude
        data['latitude'] = self.latitude

        data["timestamp"] = time.time()
        return data

