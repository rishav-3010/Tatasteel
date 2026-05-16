import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# --- Configuration ---
NUM_ROWS = 10000  # Change this to 100,000 or 1,000,000 for a larger dataset
START_TIME = datetime(2023, 10, 1, 8, 0, 0)
MOTOR_ID = "ROT-MILL-05"

# --- Simulation Parameters ---
# Nominal values for a 415V, 50Hz, 30kW Roller Table Motor
base_current = 45.0  # Amps (Idling)
load_current = 85.0  # Amps (Loaded with Steel Slab)
base_temp = 65.0     # °C
base_rpm = 1480      # RPM

# Lists to store data
data = []

current_time = START_TIME
winding_temp = base_temp
bearing_temp = base_temp - 5
is_loaded = False
load_counter = 0

print(f"Generating {NUM_ROWS} rows of synthetic data...")

for i in range(NUM_ROWS):
    # 1. Simulate "Slab Passing" (Cyclic Loading)
    # Every 50-100 cycles, a slab hits the roller (Load increases)
    if load_counter <= 0:
        is_loaded = not is_loaded
        load_counter = random.randint(20, 100) # Duration of state
    load_counter -= 1

    # 2. Generate Parameters based on Load State
    if is_loaded:
        # Slab is ON the roller
        current = np.random.normal(load_current, 2.5)  # High current
        rpm = np.random.normal(base_rpm - 15, 5)       # RPM dips slightly
        vib = np.random.normal(4.5, 0.5)               # Higher vibration under load
        target_temp = 85.0                             # Motor heats up
    else:
        # Slab is OFF (Idling)
        current = np.random.normal(base_current, 1.5)  # Low current
        rpm = np.random.normal(base_rpm, 2)            # Nominal RPM
        vib = np.random.normal(1.2, 0.2)               # Low vibration
        target_temp = 60.0                             # Motor cools down

    # 3. Physics Simulation (Lagging Indicators)
    # Temperature doesn't change instantly; it trends towards target
    winding_temp += (target_temp - winding_temp) * 0.05 + np.random.normal(0, 0.1)
    bearing_temp += (target_temp - 10 - bearing_temp) * 0.03 + np.random.normal(0, 0.05)

    # 4. Environmental & Other Factors
    voltage = np.random.normal(415, 3)                 # 415V +/- fluctuations
    coolant_press = np.random.normal(4.0, 0.1)         # 4 Bar pressure
    humidity = np.random.normal(75, 5)                 # 75% Humidity (steamy mill)
    
    # Introduce occasional anomalies (Random spikes)
    
    # Simulate a systemic fault that affects multiple sensors simultaneously
    system_fault = random.random() < 0.005  # Increased to 0.5% chance

    # Vibration spike
    if system_fault or random.random() < 0.002:
        vib += 8.0  # Increased spike to ensure it crosses threshold

    # Winding temperature spike
    if system_fault or random.random() < 0.002:
        winding_temp += random.uniform(25, 40) # Increased spike to ensure it crosses threshold

    # Bearing temperature spike
    if system_fault or random.random() < 0.002:
        bearing_temp += random.uniform(20, 30) # Increased spike to ensure it crosses threshold
    
    # 5. Append Record
    data.append([
        current_time,
        MOTOR_ID,
        round(current, 2),
        round(voltage, 1),
        round(rpm, 1),
        round(vib, 3),
        round(winding_temp, 2),
        round(bearing_temp, 2),
        round(coolant_press, 2),
        round(humidity, 1)
    ])

    current_time += timedelta(seconds=1) # 1-second interval

# --- Create DataFrame ---
columns = [
    "Timestamp", "Motor_ID", "Current_Amp", "Voltage_V", 
    "Motor_RPM", "Vibration_mm_s", "Winding_Temp_C", 
    "Bearing_Temp_C", "Coolant_Pressure_Bar", "Ambient_Humidity_Pct"
]

df = pd.DataFrame(data, columns=columns)

# --- Save to CSV ---
df.to_csv("tata_steel_rot_motor_proxy.csv", index=False) 
print("Dataset Generation Complete.")
print(df.head(1000))