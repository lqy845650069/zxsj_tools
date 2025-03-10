import os, json

CONFIG_FILE = os.path.join("resources", "data", "config.json")

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class Config:
    def __init__(self):
        self.config = json.load(open(CONFIG_FILE))

    def get(self, key):
        return self.config[key] if key in self.config else None
