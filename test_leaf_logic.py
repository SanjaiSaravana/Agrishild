import sys
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

sys.path.append(r"c:\Users\91894\OneDrive\Desktop\Agrishild\pest and disease")
try:
    from app import check_color_anomalies
    
    # Test 1: Healthy green leaf (R low, G high, B low)
    img_green = Image.new('RGB', (224, 224), color=(50, 150, 50))
    print("Test 1 (Healthy Green): Is anomalous?", check_color_anomalies(img_green))
    
    # Test 2: Yellowish/Brown leaf (R high, G medium, B low)
    img_yellow = Image.new('RGB', (224, 224), color=(180, 150, 40))
    print("Test 2 (Yellow/Brown): Is anomalous?", check_color_anomalies(img_yellow))
    
    # Test 3: Dark background (R low, G low, B low)
    img_dark = Image.new('RGB', (224, 224), color=(20, 20, 20))
    print("Test 3 (Dark Background): Is anomalous?", check_color_anomalies(img_dark))
    
except Exception as e:
    print(f"Error testing: {e}")
