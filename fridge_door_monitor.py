import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
import json
import os

class FridgeDoorMonitor(hass.Hass):

    def initialize(self):
        self.log("FridgeDoorMonitor initialized ✅")

        # Entities
        self.door_sensor = "binary_sensor.door_sensor_door" # Fridge Door Sensor
        self.fridge_temp_sensor = "sensor.temp_humidity_sensor_2_temperature"  # Fridge Temp Sensor

        # Log file
        self.log_file = "/config/logs/fridge_door_events.jsonl"

        # Setup directory
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # Listen for state changes on door sensor
        self.listen_state(self.door_state_changed, self.door_sensor)

    def door_state_changed(self, entity, attribute, old, new, kwargs):
        self.log(f"Door state changed: {old} -> {new}")

        if new == "on":  # Door opened
            self.log_temp_event("door_opened")

        elif new == "off":  # Door closed
            self.log_temp_event("door_closed")
            self.run_in(self.log_delayed_temp, 30)  # 30 seconds later

    def log_temp_event(self, event_type):
        try:
            temp = float(self.get_state(self.fridge_temp_sensor))
            timestamp = datetime.now().isoformat()
            entry = {
                "timestamp": timestamp,
                "event": event_type,
                "temperature": temp
            }
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

            self.log(f"Logged {event_type} with temperature: {temp}°C")

        except Exception as e:
            self.log(f"Error logging {event_type}: {e}", level="ERROR")

    def log_delayed_temp(self, kwargs):
        self.log_temp_event("30s_after_door_closed")
