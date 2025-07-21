import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta

class SmartRelayController(hass.Hass):

    def initialize(self):
        self.log("SmartRelayController Initialized...")

        self.fridge_temp_upper_limit = float(self.get_state("input_number.fridge_temp_upper_limit"))
        self.fridge_temp_lower_limit = float(self.get_state("input_number.fridge_temp_lower_limit"))
        self.fm_temp_upper_limit = float(self.get_state("input_number.fm_temp_upper_limit"))
        self.fm_temp_lower_limit = float(self.get_state("input_number.fm_temp_lower_limit"))

        self.listen_state(self.update_thresholds, "input_number.fridge_temp_upper_limit")
        self.listen_state(self.update_thresholds, "input_number.fridge_temp_lower_limit")
        self.listen_state(self.update_thresholds, "input_number.fm_temp_upper_limit")
        self.listen_state(self.update_thresholds, "input_number.fm_temp_lower_limit")

        self.log(f"Initialized with: Fridge Upper Limit={self.fridge_temp_upper_limit}, Fridge Lower Limit={self.fridge_temp_lower_limit} \n FM Upper Limit={self.fm_temp_upper_limit}, FM Lower Limit={self.fm_temp_lower_limit}")

        # Entities
        self.FM_pump = "switch.fm_pump"
        self.FM_compressor = "switch.fm_compressor"
        self.FridgeMate_sensor = "sensor.fridgemate_sensor_temperature"
        self.fridge_sensor = "sensor.fridge_sensor_temperature"
        self.tariff_entity = "input_boolean.low_tariff" # low tariff entity, is true when low tariff is active

        # Start periodic control check
        self.run_every(self.control_logic_compressor, datetime.now(), 10)
        self.run_every(self.control_logic_fridge, datetime.now() + timedelta(seconds=5), 10)
        self.log("Control loop scheduled to run every 10 seconds.")


    def update_thresholds(self, entity, attribute, old, new, kwargs):
        self.fridge_temp_upper_limit = float(self.get_state("input_number.fridge_temp_upper_limit"))
        self.fridge_temp_lower_limit = float(self.get_state("input_number.fridge_temp_lower_limit"))
        self.fm_temp_upper_limit = float(self.get_state("input_number.fm_temp_upper_limit"))
        self.fm_temp_lower_limit = float(self.get_state("input_number.fm_temp_lower_limit"))
        self.log(f"Updated thresholds: Fridge Upper Limit={self.fridge_temp_upper_limit}, Fridge Lower Limit={self.fridge_temp_lower_limit} \n FM Upper Limit={self.fm_temp_upper_limit}, FM Lower Limit={self.fm_temp_lower_limit} ")


    def control_logic_compressor(self, kwargs):
        try:
            # Fetch low tariff state
            low_tariff_now = self.get_state(self.tariff_entity)

            # Fetch current temperatures
            FridgeMate_temp = float(self.get_state(self.FridgeMate_sensor))
            fridge_temp = float(self.get_state(self.fridge_sensor))

            self.log(f"[READINGS] Fridge Mate Temp: {FridgeMate_temp}°C | Fridge Temp: {fridge_temp}°C | Low Tariff: {low_tariff_now}")

            # --- FM_compressor Cooling mehanism for coolant material control: run until temperature ≤ lower threshold ---
            if low_tariff_now and FridgeMate_temp > self.fm_temp_lower_limit:
                self.log(
                    f"Fridge Mate Temp ({FridgeMate_temp}°C) > lower threshold "
                    f"({self.fm_temp_lower_limit}°C). AND \n "
                    f"Low Tariff is {low_tariff_now}, Turning ON compressor to cool coolant material"
                )
                self.turn_on(self.FM_compressor)
            elif low_tariff_now and FridgeMate_temp <= self.fm_temp_lower_limit:
                self.log(
                    f"Fridge Mate Temp ({FridgeMate_temp}°C) ≤ lower threshold "
                    f"({self.fm_temp_lower_limit}°C). Cooling capacity at MAX, Turning OFF compressor."
                )
                self.turn_off(self.FM_compressor)
            elif FridgeMate_temp > self.fm_temp_upper_limit:
                self.log(
                    f"Fridge Mate Temp ({FridgeMate_temp}°C) > Upper threshold "
                    f"({self.fm_temp_upper_limit}°C).\n Coolant needs to be cooled Turning ON compressor to cool coolant material"
                )
                self.turn_on(self.FM_compressor)
            else: 
                self.log(
                    f"Low Tarrif is {low_tariff_now}, Turning OFF compressor."
                )
                self.turn_off(self.FM_compressor)
        
        except Exception as e:
            self.log(f"Error in control_logic: {e}", level="ERROR")


    def control_logic_fridge(self, kwargs):
        try:
            FidgeMate_temp = float(self.get_state(self.FridgeMate_sensor))
            fridge_temp = float(self.get_state(self.fridge_sensor))

            self.log(f"[READINGS] Fridge Mate Temp: {FidgeMate_temp}°C | Fridge Temp: {fridge_temp}°C")

            # --- FM_coolant pump control: run while fridge_temp is between lower and upper thresholds ---
            if fridge_temp >= self.fridge_temp_upper_limit:
                self.log(
                    f"Fridge Temp: {fridge_temp}°C > Upper Threshold, Turning ON Fridge Mate Pump"
                )
                self.turn_on(self.FM_pump)
            elif fridge_temp <= self.fridge_temp_lower_limit:
                self.log(
                    f"Fridge Temp: {fridge_temp}°C < Lower Threshold, Turning OFF Fridge Mate Pump."
                )
                self.turn_off(self.FM_pump)
            else:
                self.log(
                    f"Fridge Temp: {fridge_temp}°C  within the acceptable range. Turning OFF Fridge Mate Pump"
                )
                self.turn_on(self.FM_pump)
    
        except Exception as e:
            self.log(f"Error in control_logic_fridge: {e}", level="ERROR")





# import appdaemon.plugins.hass.hassapi as hass
# from datetime import datetime

# class SmartRelayController(hass.Hass):

#     def initialize(self):
#         self.log("SmartRelayController Initialized ✅")

#         # Setpoints
#         self.set_fridge_temp_diff = float(self.args.get("set_fridge_temp_diff", 1.0))
#         self.set_fridge_temp_value = float(self.args.get("set_fridge_temp_value", 25.0))

#         # Entities
#         self.coolant_plug = "switch.smart_plug"
#         # self.compressor_plug = "switch.smart_plug_compressor"
#         self.coolant_sensor = "sensor.temp_humidity_sensor_1_temperature"
#         self.fridge_sensor = "sensor.temp_humidity_sensor_2_temperature"
#         self.tariff_entity = "input_boolean.high_tariff"

#         # Set tariff to on at startup
#         self.set_state(self.tariff_entity, state="on")
#         self.log("Tariff entity set to 'on' at initialization.")

#         # Start periodic control check
#         self.run_every(self.control_logic, datetime.now(), 60)
#         self.log("Control loop scheduled to run every 60 seconds.")

#     def control_logic(self, kwargs):
#         try:
#             high_tariff_now = self.get_state(self.tariff_entity) == "on"
#             coolant_temp = float(self.get_state(self.coolant_sensor))
#             fridge_temp = float(self.get_state(self.fridge_sensor))

#             self.log(f"[READINGS] Tariff: {'High' if high_tariff_now else 'Low'} | "
#                      f"Coolant Temp: {coolant_temp}°C | Fridge Temp: {fridge_temp}°C")

#             if fridge_temp >= self.set_fridge_temp_value:
#                 self.log("Fridge temp exceeds set threshold.")

#                 if high_tariff_now and coolant_temp <= (self.set_fridge_temp_value - self.set_fridge_temp_diff):
#                     self.log("High tariff AND coolant temp is cold enough. Turning OFF compressor.")
#                     # self.turn_off(self.compressor_plug)

#                     if fridge_temp >= coolant_temp:
#                         self.log("Fridge warmer than coolant. Turning ON coolant plug.")
#                         self.turn_on(self.coolant_plug)
#                     elif fridge_temp < (coolant_temp - self.set_fridge_temp_diff):
#                         self.log("Fridge cooler than coolant significantly. Turning OFF coolant plug.")
#                         self.turn_off(self.coolant_plug)
#                 else:
#                     self.log("Either tariff is low OR coolant temp is not cold enough. Turning OFF coolant.")
#                     self.turn_off(self.coolant_plug)

#                     # if fridge_temp >= self.set_fridge_temp_value:
#                     #     self.log("Fridge still above threshold. Turning ON compressor.")
#                     #     self.turn_on(self.compressor_plug)
#                     # elif fridge_temp < (self.set_fridge_temp_value - self.set_fridge_temp_diff):
#                     #     self.log("Fridge below cooling margin. Turning OFF compressor.")
#                     #     self.turn_off(self.compressor_plug)
#             else:
#                 self.log("Fridge temp is within acceptable limits. Turning OFF both coolant and compressor.")
#                 self.turn_off(self.coolant_plug)
#                 # self.turn_off(self.compressor_plug)

#         except Exception as e:
#             self.log(f"⚠ Error in control_logic: {e}", level="ERROR")




# import appdaemon.plugins.hass.hassapi as hass
# from datetime import datetime, timedelta

# class SmartRelayController(hass.Hass):

#     def initialize(self):
#         self.log("SmartRelayController Initialized... ")

#         # Centralized entity ID mapping
#         self.entity_ids = {
#             "fm_pump": "switch.fm_pump",
#             "fm_compressor": "switch.fm_compressor",
#             "fridge01_sensor": "sensor.fridge01_temperature",
#             "fm_sensor": "sensor.fridgemate_temperature",
#             "low_tariff": "input_boolean.low_tariff",
#             "fridge_temp_upper_limit": "input_number.fridge01_temp_upper_limit",
#             "fridge_temp_lower_limit": "input_number.fridge01_temp_lower_limit",
#             "fm_temp_upper_limit": "input_number.fm_temp_upper_limit",
#             "fm_temp_lower_limit": "input_number.fm_temp_lower_limit"
#         }

#         self.log("Loading temperature thresholds from input_numbers...")
#         self.load_thresholds()

#         self.log("Setting up listeners for threshold updates...")
#         for threshold_key in ["fridge_temp_upper_limit", "fridge_temp_lower_limit", "fm_temp_upper_limit", "fm_temp_lower_limit"]:
#             self.listen_state(self.update_thresholds, self.entity_ids[threshold_key])

#         self.log("Scheduling control loops...")
#         self.run_every(self.control_logic_compressor, datetime.now(), 10)
#         self.run_every(self.control_logic_fridge, datetime.now() + timedelta(seconds=5), 10)
#         self.log("Control loops scheduled to run every 10 seconds.")

#     def load_thresholds(self):
#         try:
#             self.thresholds = {
#                 "fridge_temp_upper_limit": float(self.get_state(self.entity_ids["fridge_temp_upper_limit"])),
#                 "fridge_temp_lower_limit": float(self.get_state(self.entity_ids["fridge_temp_lower_limit"])),
#                 "fm_temp_upper_limit": float(self.get_state(self.entity_ids["fm_temp_upper_limit"])),
#                 "fm_temp_lower_limit": float(self.get_state(self.entity_ids["fm_temp_lower_limit"]))
#             }
#             self.log(
#                 f"Thresholds Loaded: Fridge [{self.thresholds['fridge_temp_lower_limit']}°C, {self.thresholds['fridge_temp_upper_limit']}°C], "
#                 f"Coolant [{self.thresholds['fm_temp_lower_limit']}°C, {self.thresholds['fm_temp_upper_limit']}°C]")
#         except Exception as e:
#             self.log(f"Failed to load thresholds: {e}", level="ERROR")

#     def update_thresholds(self, entity, attribute, old, new, kwargs):
#         self.load_thresholds()
#         self.log("Thresholds updated due to input_number change.")

#     def get_sensor_float(self, entity_id):
#         value = self.get_state(entity_id)
#         if value not in [None, "unknown", "unavailable"]:
#             try:
#                 return float(value)
#             except ValueError:
#                 self.log(f"Cannot convert value of {entity_id} to float: {value}", level="WARNING")
#         else:
#             self.log(f"Sensor {entity_id} returned invalid state: {value}", level="WARNING")
#         return None

#     def control_logic_compressor(self, kwargs):
#         try:
#             low_tariff = self.get_state(self.entity_ids["low_tariff"])
#             coolant_temp = self.get_sensor_float(self.entity_ids["fm_sensor"])

#             if None in [coolant_temp, low_tariff]:
#                 self.log("Missing data for compressor logic. Skipping execution.", level="WARNING")
#                 return

#             self.log(f"[Compressor Check] Coolant Temp: {coolant_temp}°C | Low Tariff: {low_tariff}")

#             if low_tariff == "on" and coolant_temp > self.thresholds["fm_temp_lower_limit"]:
#                 self.turn_on(self.entity_ids["fm_compressor"])
#                 self.log("Turning ON FM Compressor (Coolant temp above lower limit and low low_tariff ON)")
#             elif low_tariff == "on" and coolant_temp <= self.thresholds["fm_temp_lower_limit"]:
#                 self.turn_off(self.entity_ids["fm_compressor"])
#                 self.log("Turning OFF FM Compressor (Coolant temp at or below lower limit and low low_tariff ON)")
#             elif coolant_temp > self.thresholds["fm_temp_upper_limit"]:
#                 self.turn_on(self.entity_ids["fm_compressor"])
#                 self.log("Turning ON FM Compressor (Coolant temp above upper limit)")
#             else:
#                 self.turn_off(self.entity_ids["fm_compressor"])
#                 self.log("Turning OFF FM Compressor (Conditions not met)")

#         except Exception as e:
#             self.log(f"Error in control_logic_compressor: {e}", level="ERROR")

#     def control_logic_fridge(self, kwargs):
#         try:
#             fridge_temp = self.get_sensor_float(self.entity_ids["fridge01_sensor"])

#             if fridge_temp is None:
#                 self.log("Missing fridge temperature. Skipping fridge logic.", level="WARNING")
#                 return

#             self.log(f"[Fridge Check] Fridge Temp: {fridge_temp}°C")

#             if fridge_temp >= self.thresholds["fridge_temp_upper_limit"]:
#                 self.turn_on(self.entity_ids["fm_pump"])
#                 self.log("Turning ON FM Pump (Fridge temp above upper threshold)")
#             elif fridge_temp <= self.thresholds["fridge_temp_lower_limit"]:
#                 self.turn_off(self.entity_ids["fm_pump"])
#                 self.log("Turning OFF FM Pump (Fridge temp below lower threshold)")
#             else:
#                 self.turn_off(self.entity_ids["fm_pump"])
#                 self.log("FM Pump OFF (Fridge temp within acceptable range)")

#         except Exception as e:
#             self.log(f"Error in control_logic_fridge: {e}", level="ERROR")
