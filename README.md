
# FridgeMate – Smart Refrigerator Automation & Monitoring

![Architecture Diagram](A_flowchart_in_the_image_illustrates_a_smart_refri.png)

FridgeMate is an **intelligent refrigeration automation project** built on **Home Assistant OS** using **AppDaemon apps**. It optimizes energy usage, monitors door events, logs sensor data locally, and syncs data to a cloud database (Firestore).

---

## **Overview**

FridgeMate enhances refrigeration efficiency by:
- **Monitoring fridge and coolant temperatures** via sensors.
- **Controlling relays (pump and compressor)** using smart plugs.
- **Logging door events and sensor readings** locally in `.jsonl` files.
- **Batching and sending logs** to a remote API (Firestore backend).
- Leveraging **low-tariff periods** for pre-cooling and energy optimization.

The project is designed to be **sensor-agnostic** – any temperature or door sensors can be used as long as their **Home Assistant entity IDs** are provided.

---

## **Features**
- **AppDaemon Automations**:
  - `control_relay.py` – Controls pump & compressor based on temperature thresholds and tariff status.
  - `fridge_door_monitor.py` – Logs door open/close events and temperatures.
  - `sensor_logger.py` – Logs temperature, humidity, and smart plug data every minute, and uploads logs to Firestore every 20 minutes.
- **Local Logging**:
  - Sensor data stored in `/config/logs/sensors_logs.jsonl`.
  - Door events logged in `/config/logs/fridge_door_events.jsonl`.
- **Cloud Sync**:
  - Periodic POST requests to Firestore API for remote storage.
- **Energy Optimization**:
  - Intelligent compressor/pump control during low-tariff hours.
- **Home Assistant OS Integration**:
  - Apps are deployed under `/config/appdaemon/apps`.

---

## **System Architecture**

The system is composed of:
- **Sensors**: Temperature & door sensors (any Home Assistant compatible devices).
- **Smart Plugs**: To control fridge components (e.g., compressor, pump).
- **Home Assistant OS**: Central automation hub.
- **AppDaemon**: Runs Python scripts for control logic & data logging.
- **Firestore**: Cloud storage for logs and analytics.

Refer to the diagram above for a high-level overview.

---

## **Directory Structure**

```
/config/appdaemon/apps/
│
├── control_relay.py        # Relay logic for compressor & pump
├── fridge_door_monitor.py  # Logs door open/close events
└── sensor_logger.py        # Sensor data logger and Firestore sync
```

---

## **Installation & Setup**

1. **Install Home Assistant OS** on Raspberry Pi (or any supported device).
2. **Enable AppDaemon Add-on** in Home Assistant.
3. Clone this repository into the Home Assistant `addon_configs/appdaemon/apps` directory:
   ```bash
   git clone https://github.com/<your-username>/fridgemate.git /config/appdaemon/apps/fridgemate
   ```
4. Add entries to `apps.yaml`:
   ```yaml
   control_relay:
     module: control_relay
     class: SmartRelayController

   fridge_door_monitor:
     module: fridge_door_monitor
     class: FridgeDoorMonitor

   sensor_logger:
     module: sensor_logger
     class: SensorLogger
   ```
5. **Update entity IDs** in the Python scripts according to your Home Assistant sensor and smart plug names.
6. Restart AppDaemon to activate the apps.

---

## **Configuration**

- **Temperature thresholds** are read from `input_number` entities in Home Assistant:
  - `input_number.fridge_temp_upper_limit`
  - `input_number.fridge_temp_lower_limit`
  - `input_number.fm_temp_upper_limit`
  - `input_number.fm_temp_lower_limit`
- **API URL**: Update `self.api_url` in `sensor_logger.py` to your Firestore POST endpoint.
- **Log files** are stored under `/config/logs/`.


---



## **License**
This project is proprietary and intended for portfolio demonstration.  
**All Rights Reserved – commercial use or redistribution without permission is prohibited.**

---

## **Author**
Developed by **[Muhammad Uzaif and Hafsa Javed]** as part of an IoT and automation project for refrigeration systems.

---
