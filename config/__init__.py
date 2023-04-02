from . import *
import yaml
def load():
    with open('config/config.yaml','r',encoding='utf-8') as f:
        config = yaml.load(f)
        return config