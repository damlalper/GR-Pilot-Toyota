import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the main app
from main import get_suggestions, get_driver_dna, get_pit_strategy

# Test suggestions endpoint
print("Testing suggestions endpoint...")
try:
    result = get_suggestions(lap=5)
    print("SUCCESS:", result)
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()

print("\n" + "="*50 + "\n")

# Test driver_dna endpoint
print("Testing driver_dna endpoint...")
try:
    result = get_driver_dna(lap=5)
    print("SUCCESS:", result)
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()

print("\n" + "="*50 + "\n")

# Test pit_strategy endpoint
print("Testing pit_strategy endpoint...")
try:
    result = get_pit_strategy(lap=5)
    print("SUCCESS:", result)
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()
