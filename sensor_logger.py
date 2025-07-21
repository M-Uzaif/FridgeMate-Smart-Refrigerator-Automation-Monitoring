import appdaemon.plugins.hass.hassapi as hass
import json
import os
from datetime import datetime, timedelta
import requests

class SensorLogger(hass.Hass):

    def initialize(self):
        self.log("SensorLogger App Initialized ")

        self.log_file = "/config/logs/sensors_logs.jsonl"
        self.api_url = "https://api-xh7tmp3cta-uc.a.run.app/addUserData"  # <--- REPLACE THIS

        # Start periodic logging and batching after HA has initialized
        self.run_in(self.start_logging, 30)

    def start_logging(self, kwargs):
        self.log("Starting periodic logging after 30s delay ⏱")
        self.run_every(self.log_sensor_data, datetime.now(), 60)        # every minute
        self.run_every(self.send_batched_logs, datetime.now(), 1200)    # every 20 minutes

    def log_sensor_data(self, kwargs):
        self.log("Collecting data...")

        # Get state + unit for each sensor
        def get_state_and_unit(entity_id):
            state = self.get_state(entity_id)
            attrs = self.get_state(entity_id, attribute="all")
            unit = attrs.get("attributes", {}).get("unit_of_measurement") if attrs else None
            return {"value": state, "unit": unit}

        data = {
            "timestamp": datetime.now().isoformat(),
            "Coolant_Box_Temperature": get_state_and_unit("sensor.temp_humidity_sensor_1_temperature"),
            "Fridge_Temperature": get_state_and_unit("sensor.temp_humidity_sensor_2_temperature"),
            "Coolant_Box_Humidity": get_state_and_unit("sensor.temp_humidity_sensor_1_humidity"),
            "Fridge_Humidity": get_state_and_unit("sensor.temp_humidity_sensor_2_humidity"),
            "Plug_Status": {"value": self.get_state("switch.smart_plug"), "unit": None},
            "Plug_Current": get_state_and_unit("sensor.smart_plug_current"),
            "Plug_Voltage": get_state_and_unit("sensor.smart_plug_voltage"),
            "Plug_Current_Consumption": get_state_and_unit("sensor.smart_plug_current_consumption"),
            "Plug_Todays_Consumption": get_state_and_unit("sensor.smart_plug_today_s_consumption")
        }

        self.log("Collected Data:\n" + json.dumps(data, indent=2), level="INFO")

        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        except Exception as e:
            self.log(f"Failed to create log directory: {e}", level = "ERROR")
            return

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(data) + "\n")
            self.log(f"Logged sensor data at {data['timestamp']}")
        except Exception as e:
            self.log(f"Failed to write log file: {e}", level = "ERROR")

    def send_batched_logs(self, kwargs):
        self.log("Preparing to send batched logs to remote server...")

        if not os.path.exists(self.log_file):
            self.log("No log file found, skipping batch send.")
            return

        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()
            logs = [json.loads(line) for line in lines if line.strip()]
        except Exception as e:
            self.log(f"Failed to read log file for batching: {e}", level="ERROR")
            return

        if not logs:
            self.log("Log file is empty, nothing to send.")
            return

        payload = {
            "uid": "Uzaif_HA",
            "logs": logs
        }
        headers = { "Content-Type": "application/json" }

        # 🔹 Save the payload to external file for backend team
        # try:
        #     with open("/config/last_payload.json", "w") as f:
        #         json.dump(payload, f, indent=2)
        #     self.log("Saved outgoing payload to /config/logs/last_payload.json")
        # except Exception as e:
        #     self.log(f"Failed to save payload file: {e}", level="ERROR")

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            self.log(f"Successfully sent {len(logs)} logs to server")

            # Clear the log file after success
            open(self.log_file, "w").close()

        except Exception as e:
            self.log(f"Failed to send logs (1st attempt): {e}", level="ERROR")
            self.run_in(self.retry_send_logs, 20, logs=logs)

    def retry_send_logs(self, kwargs):
        logs = kwargs.get("logs")
        if not logs:
            self.log("No logs provided for retry.", level = "ERROR")
            return

        payload = {  
            "uid": "Uzaif_HA",
            "data": logs }
        headers = { "Content-Type": "application/json" }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            self.log(f"Retry succeeded: Sent {len(logs)} logs to server ")

            # Clear the local log file after successful retry
            open(self.log_file, "w").close()

        except Exception as e:
            self.log(f"Retry failed: {e}",level = "ERROR")




## Below is the starter version that was only responsible for storing data localy after every minute
# import appdaemon.plugins.hass.hassapi as hass
# import json
# import os
# from datetime import datetime, timedelta

# class SensorLogger(hass.Hass):

#     def initialize(self):
#         self.log("SensorLogger App Initialized !!")

#         # Delay actual logging to allow HA to finish initializing all entities
#         self.run_in(self.start_logging, 30)

#     def start_logging(self, kwargs):
#         self.log("Starting periodic logging after 30s delay...")
#         self.run_every(self.log_sensor_data, datetime.now(), 60)

#     def get_state_with_unit(self, entity_id):
#         """Helper to return value + unit dict for a given entity."""
#         return {
#             "value": self.get_state(entity_id),
#             "unit": self.get_state(entity_id, attribute="unit_of_measurement")
#         }

#     def log_sensor_data(self, kwargs):
#         self.log("Collecting data...")


#         # # List of entities to verify availability
#         # entities = [
#         #     "sensor.temp_humidity_sensor_1_temperature",
#         #     "sensor.temp_humidity_sensor_1_humidity",
#         #     "sensor.temp_humidity_sensor_2_temperature",
#         #     "sensor.temp_humidity_sensor_2_humidity",
#         #     "switch.smart_plug",
#         #     "sensor.smart_plug_current",
#         #     "sensor.smart_plug_voltage",
#         #     "sensor.smart_plug_current_consumption",
#         #     "sensor.smart_plug_today_s_consumption"
#         # ]

#         # # Log state of each entity for debugging
#         # for eid in entities:
#         #     value = self.get_state(eid)
#         #     self.log(f"Entity check: {eid} → {value}")

        
#         # Collect value and unit for each relevant sensor
#         data = {
#             "timestamp": datetime.now().isoformat(),
#             "Coolant_Box_Temperature": self.get_state_with_unit("sensor.temp_humidity_sensor_1_temperature"),
#             "Fridge_Temperature": self.get_state_with_unit("sensor.temp_humidity_sensor_2_temperature"),
#             "Coolant_Box_Humidity": self.get_state_with_unit("sensor.temp_humidity_sensor_1_humidity"),
#             "Fridge_Humidity": self.get_state_with_unit("sensor.temp_humidity_sensor_2_humidity"),
#             "Plug_Status": {"value": self.get_state("switch.smart_plug")},  # Switches don't have units
#             "Plug_Current": self.get_state_with_unit("sensor.smart_plug_current"),
#             "Plug_Voltage": self.get_state_with_unit("sensor.smart_plug_voltage"),
#             "Plug_Current_Consumption": self.get_state_with_unit("sensor.smart_plug_current_consumption"),
#             "Plug_Todays_Consumption": self.get_state_with_unit("sensor.smart_plug_today_s_consumption")
#         }

#         # Log the collected data before writing
#         self.log("Collected Data:\n" + json.dumps(data, indent=2), level="INFO")

#         # Path for log file in /config/logs
#         log_path = "/config/logs/sensors_logs.jsonl"

#         try:
#             # Ensure directory exists
#             os.makedirs(os.path.dirname(log_path), exist_ok=True)
#             self.log(f"file created at path {log_path}...")
#         except Exception as e:
#             self.log(f"Failed to create directory for log file: {e}")
#             return

#         try:
#             # Append data to the log file
#             with open(log_path, "a") as f:
#                 f.write(json.dumps(data) + "\n")
#             self.log(f"Logged sensor data at {data['timestamp']}")
#         except Exception as e:
#             self.log(f"Failed to write to log file at {log_path}: {e}")
