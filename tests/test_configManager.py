import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app.configManager import ConfigManager, ConfigValidationError

schema = 'app/config.schema.yaml'
test_config_root_folder = 'tests/test_configs'

def test_example_config():
    cm = ConfigManager(schema, 'app/config.example.yaml')

def test_valid_full_config():
    cm = ConfigManager(schema, f'{test_config_root_folder}/valid.full.yaml')
    
def test_valid_min_config():
    cm = ConfigManager(schema, f'{test_config_root_folder}/valid.min.yaml')
    
def test_valid_assignee_email_config():
    cm = ConfigManager(schema, f'{test_config_root_folder}/valid.assignee_email.yaml')
    
def test_invalid_assignee_email_config():
    with pytest.raises(ConfigValidationError):
        cm = ConfigManager(schema, f'{test_config_root_folder}/invalid.assignee_email.yaml')
        
def test_invalid_missing_option_config():
    with pytest.raises(ConfigValidationError):
        cm = ConfigManager(schema, f'{test_config_root_folder}/invalid.missing_option.yaml')

def test_invalid_wrong_option_config():
    with pytest.raises(ConfigValidationError):
        cm = ConfigManager(schema, f'{test_config_root_folder}/invalid.wrong_option.yaml')
        