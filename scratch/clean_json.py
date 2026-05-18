import json
import math

def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean(x) for x in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj

try:
    with open('dashboard/public/data/opportunities.json', 'r') as f:
        content = f.read().replace('NaN', 'null')
        data = json.loads(content)
    
    clean_data = clean(data)
    
    with open('dashboard/public/data/opportunities.json', 'w') as f:
        json.dump(clean_data, f, indent=2)
    
    # Also fix the data/ folder one
    with open('data/opportunities.json', 'w') as f:
        json.dump(clean_data, f, indent=2)
        
    print("JSON cleaned successfully.")
except Exception as e:
    print(f"Error: {e}")
