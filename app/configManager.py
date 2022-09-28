import logging
import yaml
import os
import yamale

log = logging.getLogger(__name__)
SCHEMA = './config.schema.yaml'

class ConfigManager():
    def __init__(self, path_to_config):
        """Initialize config.

        Args:
            path_to_config (str): path to config.yaml
        """
        self.path_to_config = path_to_config
        self.schema = yamale.make_schema(SCHEMA)
        self._cached_st_mtime = os.stat(path_to_config).st_mtime
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
        self.validate_configuration()
        try:
            with open(self.path_to_config, 'r') as yamlfile:
                self._config = yaml.safe_load(yamlfile)
                log.info(f'updated config: {self.path_to_config}')
        except Exception as ex:
            log.error(f"could not load configuration '{ex}'")
        
            
    def validate_configuration(self):
        """Validate config.yaml
        """
        data = yamale.make_data(self.path_to_config)
        try:
            log.info(f"validating configuration with schema '{SCHEMA}'")
            yamale.validate(self.schema, data)
            log.info('validation passed 👍')
        except yamale.YamaleError as ex:
            log.error('validation failed!')
            for result in ex.results:
                log.error(f"Error validating data '{result.data}' with '{result.schema}'")
                for error in result.errors:
                    log.error(f" -> {error}")
            exit(1)
            
    @property
    def config(self):
        """Get config

        Returns:
            dict: deserialized config.yaml
        """
        return self._config
