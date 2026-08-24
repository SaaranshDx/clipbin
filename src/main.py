PASTES_PATH = "../db/"
PASTES_META_PATH = f"{PASTES_PATH}/meta"


def create_paste(id, data):
    try:
        with open(f"{PASTES_PATH}/{id}", "w", encoding="utf-8") as f:
            f.write(data)
        return True
    except Exception as e:
        return False 