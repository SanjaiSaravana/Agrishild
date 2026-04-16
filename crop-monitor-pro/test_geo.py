import sys
sys.path.append(r"c:\Users\91894\OneDrive\Desktop\Agrishild\crop-monitor-pro\src\collectors")
import gee_api

# Test 1: Valid Land Location (Somewhere in California farm with sensors)
print("--- Test 1: Valid Land (No sensors) ---")
res1 = gee_api.get_satellite_analysis(lat=36.7783, lon=-119.4179)
print(res1)

# Test 2: Valid Land but with Soil Moisture = 0 (Hard Constraint Triggered)
print("\n--- Test 2: Soil Moisture = 0 ---")
res2 = gee_api.get_satellite_analysis(lat=36.7783, lon=-119.4179, soil_moisture=0, nutrient_data={"N": 10})
print(res2)

# Test 3: Ocean Data Drop (Water Body)
print("\n--- Test 3: Ocean coordinates ---")
res3 = gee_api.get_satellite_analysis(lat=0.0, lon=0.0, soil_moisture=40, nutrient_data={"N": 10})
print(res3)
