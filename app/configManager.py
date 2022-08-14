import logging
import yaml
import os
import sys

log = logging.getLogger(__name__)

class ConfigManager():
    def __init__(self, path_to_config):
        """Initialize config.

        Args:
            path_to_config (str): path to config.yaml
        """
        self.path_to_config = path_to_config
        self._cached_st_mtime = 0
        self._config = dict()
        self.update_configuration()
        
        
    def needs_update(self) -> bool:
        """Check if config changed

        Returns:
            bool: return True if config change detected
        """
        needs_update = False
        st_mtime = os.stat(self.path_to_config).st_mtime
        if st_mtime != self._cached_st_mtime:
            log.info('config change detected')
            self._cached_st_mtime = st_mtime
            needs_update = True
        return needs_update
             
    
    def update_configuration(self):
        """Reload config.yaml
        """
        try:
            with open(self.path_to_config, 'r') as yamlfile:
                self._config = yaml.safe_load(yamlfile)
                log.info(f'updated config')
        except Exception as ex:
            log.error(f'could not load configuration: {ex}')
            
    @property
    def config(self):
        """Get config

        Returns:
            dict: deserialized config.yaml
        """
        return self._config
