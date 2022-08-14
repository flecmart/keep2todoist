import logging
import yaml
import os

log = logging.getLogger(__name__)

class Config():
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
            bool: _description_
        """
        return os.stat(self.path_to_config).st_mtime != self._cached_st_mtime
             
    
    def update_configuration(self):
        """Reload config.yaml
        """
        try:
            with open(self.path_to_config, 'r') as yamlfile:
                self._config = yaml.safe_load(yamlfile)
                # TODO: don't expose secrets
                log.info(f'updated config: {self.config}')
        except Exception as ex:
            log.error(f'Could not load configuration: {ex}')
            
            
    @property
    def config(self):
        """Get config

        Returns:
            dict: deserialized config.yaml
        """
        return self._config
