import random
import time
from enum import Enum

class Tank:
    class FlowState(Enum):
        OFF = 0
        LOW = 1
        MEDIUM = 2
        HIGH = 3

    tank_sensors_range = {
        'ORP': (-100, 1000),
        'PH': (0, 14),
        'Salinity': (0, 50000),
        'Water_Depth': (0, 8),
        'Turbidity': (0, 50.0),
        'Temperature': (-55, 150.0)
    }

    sensors_acceptable_range = {
        'ORP': (650, 700),
        'PH': (6, 8.5),
        'Salinity': (0, 600),
        'Water_Depth': (0, 8),
        'Turbidity': (0, 5.0),
        'Temperature': (25, 30.0)
    }

    def __init__(self, name:str ,longitude:float, latitude: float):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.sensors_previous_value = self.get_sensors_initial_values()
        self.sensors_current_value = self.get_sensors_initial_values()
        self.tank_outlet_state = Tank.FlowState.MEDIUM.name
        self.tank_inlet_state = Tank.FlowState.LOW.name
        self.impurity_present = False

    def get_sensors_initial_values(self):
        """Retrieve the initial values of sensors."""
        return {sensor: round(random.uniform(*self.sensors_acceptable_range[sensor]),2 )for sensor in self.sensors_acceptable_range}

    def generate_water_depth(self):
        """Simulate water depth changes based on inlet and outlet flow."""
        flow_rate_map = {
            Tank.FlowState.OFF.name: 0.0,
            Tank.FlowState.LOW.name: 0.2,
            Tank.FlowState.MEDIUM.name: 0.5,
            Tank.FlowState.HIGH.name: 0.8
        }

        inlet_flow = flow_rate_map[self.tank_inlet_state]
        outlet_flow = flow_rate_map[self.tank_outlet_state]

        # Update water depth based on net flow
        previous_water_depth = self.sensors_previous_value['Water_Depth']
        self.sensors_previous_value['Water_Depth'] = self.sensors_current_value['Water_Depth']

        net_flow = inlet_flow - outlet_flow + round(random.uniform(-0.1, 0.1),2)
        self.sensors_current_value['Water_Depth'] += net_flow * previous_water_depth

        # Ensure water depth remains within valid range
        self.sensors_current_value['Water_Depth'] = round(max(
            self.sensors_acceptable_range['Water_Depth'][0],
            min(self.sensors_current_value['Water_Depth'], self.sensors_acceptable_range['Water_Depth'][1])
        ),2)

        # Adjust related parameters as water depth increases
        if net_flow > 0:  # When water depth is increasing
            self.sensors_current_value['Turbidity'] = round(max(
                self.sensors_acceptable_range['Turbidity'][0],
                self.sensors_current_value['Turbidity'] - (self.sensors_current_value['Water_Depth'] * 0.3),2)
            )
            self.sensors_current_value['PH'] = round(max(
                self.sensors_acceptable_range['PH'][0],
                min(self.sensors_current_value['PH'] - (self.sensors_current_value['Water_Depth'] * 0.05), self.sensors_acceptable_range['PH'][1]),2)
            )
            self.sensors_current_value['Salinity'] = round(max(
                self.sensors_acceptable_range['Salinity'][0],
                self.sensors_current_value['Salinity'] - (self.sensors_current_value['Water_Depth'] * 5),2)
            )
            self.sensors_current_value['ORP'] = round(max(
                self.sensors_acceptable_range['ORP'][0],
                min(self.sensors_current_value['ORP'] - (self.sensors_current_value['Water_Depth'] * 2), self.sensors_acceptable_range['ORP'][1]),2)
            )

    def generate_sensor_value(self, sensor_name, base_effect=0, scale=1.0):
        """Generate or update a specific sensor value."""
        self.sensors_previous_value[sensor_name] = self.sensors_current_value[sensor_name]

        # Generate a dynamic random effector
        random_effector = random.uniform(-1, 1) * scale

        # Apply the effect
        self.sensors_current_value[sensor_name] += round(base_effect + random_effector,2)

        # Clamp the sensor value within the acceptable range
        self.sensors_current_value[sensor_name] = round(max(
            self.sensors_acceptable_range[sensor_name][0],
            min(self.sensors_current_value[sensor_name], self.sensors_acceptable_range[sensor_name][1]),2)
        )

    def generate_ORP(self):
        base_effect = 5 if self.impurity_present else 0
        self.generate_sensor_value('ORP', base_effect=base_effect, scale=50)

    def generate_PH(self):
        base_effect = 3 if self.impurity_present else 0
        self.generate_sensor_value('PH', base_effect=base_effect, scale=2)

    def generate_Salinity(self):
        base_effect = 10 if self.impurity_present else 0
        self.generate_sensor_value('Salinity', base_effect=base_effect, scale=1)

    def generate_turbidity(self):
        base_effect = 2 if self.impurity_present else 0
        self.generate_sensor_value('Turbidity', base_effect=base_effect, scale=0.1)

    def generate_temperature(self):
        inflow_hot = random.choice([True, False])
        base_effect = 0.5 if inflow_hot else -0.5
        self.generate_sensor_value('Temperature', base_effect=base_effect, scale=2)

    def manage_is_impurity(self):
        """Determine if impurities are present based on sensor values."""
        self.impurity_present = any([
            self.sensors_current_value['PH'] > self.sensors_acceptable_range['PH'][1],
            self.sensors_current_value['PH'] < self.sensors_acceptable_range['PH'][0],
            abs(self.sensors_previous_value['Turbidity'] - self.sensors_current_value['Turbidity']) > 3,
            self.sensors_current_value['ORP'] < self.sensors_acceptable_range['ORP'][0],
            self.sensors_current_value['ORP'] > self.sensors_acceptable_range['ORP'][1],
            self.sensors_current_value['Salinity'] > self.sensors_acceptable_range['Salinity'][1]
        ])

        # If impurities are detected, take corrective actions
        if self.impurity_present:
            self.tank_inlet_state = Tank.FlowState.HIGH.name

            # Adjust related parameters
            self.sensors_current_value['Turbidity'] = max(
                self.sensors_acceptable_range['Turbidity'][0],
                min(
                    self.sensors_current_value['Turbidity'] - (self.sensors_current_value['Water_Depth'] * 0.5),
                    self.sensors_acceptable_range['Turbidity'][1]
                )
            )
            self.sensors_current_value['PH'] = max(
                self.sensors_acceptable_range['PH'][0],
                min(self.sensors_current_value['PH'] - (self.sensors_current_value['Water_Depth'] * 0.05), self.sensors_acceptable_range['PH'][1])
            )
            self.sensors_current_value['Salinity'] = max(
                self.sensors_acceptable_range['Salinity'][0],
                min(
                    self.sensors_current_value['Salinity'] - (self.sensors_current_value['Water_Depth'] * 10),
                    self.sensors_acceptable_range['Salinity'][1]
                )
            )
            self.sensors_current_value['ORP'] = max(
                self.sensors_acceptable_range['ORP'][0],
                min(
                    self.sensors_current_value['ORP'] - (self.sensors_current_value['Water_Depth'] * 2),
                    self.sensors_acceptable_range['ORP'][1]
                )
            )
    def manage_flow_rate(self):
        """Adjust the outlet state based on water depth."""
        if self.sensors_current_value['Water_Depth'] < 1:
            self.tank_outlet_state = Tank.FlowState.OFF.name
        elif self.sensors_current_value['Water_Depth'] < 2:
            self.tank_outlet_state = Tank.FlowState.LOW.name
        elif self.sensors_current_value['Water_Depth'] < 4:
            self.tank_outlet_state = Tank.FlowState.MEDIUM.name
        else:
            self.tank_outlet_state = Tank.FlowState.HIGH.name

        # Adjust inlet dynamically if impurities are present
        if self.impurity_present:
            self.tank_inlet_state = Tank.FlowState.HIGH.name
        else:
            self.tank_inlet_state = random.choice(
                [Tank.FlowState.OFF.name, Tank.FlowState.LOW.name, Tank.FlowState.MEDIUM.name]
            )

    def generate_data(self):
        """Generate sensor data for the tank."""
        self.generate_water_depth()
        self.generate_ORP()
        self.generate_PH()
        self.generate_Salinity()
        self.generate_turbidity()
        self.generate_temperature()
        self.manage_is_impurity()
        self.manage_flow_rate()

        data = self.sensors_current_value.copy()
        data['longitude'] = self.longitude
        data['latitude'] = self.latitude
        data["timestamp"] = time.time()
        return data