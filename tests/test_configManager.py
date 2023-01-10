import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app.configManager import ConfigManager, ConfigValidationError

schema = 'app/config.schema.yaml'
config_root_folder = 'tests/test_configs'

def test_valid_full_config():
    cm = ConfigManager(schema, f'{config_root_folder}/valid.full.yaml')
    
def test_valid_min_config():
    cm = ConfigManager(schema, f'{config_root_folder}/valid.full.yaml')