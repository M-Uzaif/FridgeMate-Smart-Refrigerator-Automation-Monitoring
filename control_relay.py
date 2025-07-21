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


        self.FM_pump = "switch.fm_pump"
        self.FM_compressor = "switch.fm_compressor"
        self.FridgeMate_sensor = "sensor.fridgemate_sensor_temperature"
        self.fridge_sensor = "sensor.fridge_sensor_temperature"
        self.tariff_entity = "input_boolean.low_tariff" 


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

            low_tariff_now = self.get_state(self.tariff_entity)

            FridgeMate_temp = float(self.get_state(self.FridgeMate_sensor))
            fridge_temp = float(self.get_state(self.fridge_sensor))

            self.log(f"[READINGS] Fridge Mate Temp: {FridgeMate_temp}°C | Fridge Temp: {fridge_temp}°C | Low Tariff: {low_tariff_now}")

            
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

