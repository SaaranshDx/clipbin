import time
import json
PASTES_PATH = "../db/"
PASTES_META_PATH = f"{PASTES_PATH}/meta"


def write_metadata(Id, duration):
    try:
        meta = {
            "id": Id,
    #duration is in hours ofc
            "duration": duration,
            "created_at": time.time()
        }
        meta_str = json.dumps(meta, indent=4)
        with open(f"{PASTES_META_PATH}/id.json", "x") as f:
            f.write(meta_str)
            return True
    except Exception as e:
        return False        
            
        
def create_paste(id, data):
    try:
        with open(f"{PASTES_PATH}/{id}.txt", "w", encoding="utf-8") as f:
            f.write(data)
        return True
    except Exception as e:
        return False 
    
def read_paste(id):
    try:
        data = open(f"{PASTES_PATH}/{id}.txt") 
        return data
    except Exception as e:
        return False   