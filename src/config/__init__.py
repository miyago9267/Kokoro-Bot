import os
import json
from .cfg import load_config

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GLOBAL_CONFIG_PATH = os.path.join(
    PROJECT_ROOT,
    'config',
    'global.json'
)

global_config = None

if os.path.exists(GLOBAL_CONFIG_PATH):
    global_config = load_config(GLOBAL_CONFIG_PATH)

__all__ = ['load_config', 'global_config', 'GLOBAL_CONFIG_PATH']