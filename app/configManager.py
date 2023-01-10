import logging
import yaml
import os
import yamale

log = logging.getLogger(__name__)

class ConfigManager():
    def __init__(self, path_to_schema: str, path_to_config: str):
        """Initialize config

        Args:
            path_to_schema (str): path to config.schema.yaml
            path_to_config (str): path to config.yaml
        """
        self.path_to_schema = path_to_schema
        self.path_to_config = path_to_config
        self.schema = yamale.make_schema(path_to_schema)
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
    
    def validate_schema(self):
        """Validate against config.schema.yaml
        https://github.com/23andMe/Yamale#examples

        Raises:
            Exception: Raised in case of YamaleError
        """
        data = yamale.make_data(self.path_to_config)
        try:
            log.info(f"validating configuration with schema '{self.path_to_schema}'")
            yamale.validate(self.schema, data)
            log.info('schema validation passed 👍')
        except yamale.YamaleError as ex:
            for result in ex.results:
                log.error(f"Error validating data '{result.data}' with '{result.schema}'")
                for error in result.errors:
                    log.error(f" -> {error}")
            raise ConfigValidationError('schema validation failed ❌')
    
    def validate_configuration(self):
        """Validate config.yaml
        Raises exception and exits if validation fails
        """
        self.validate_schema()
        with open(self.path_to_config, 'r') as yamlfile:
            config = yaml.safe_load(yamlfile)
        self.validate_assignee_email(config_validate=config)
        log.info('configuration validation passed 👍')
        
    def validate_assignee_email(self, config_validate: dict):
        """For each defined list in the config, validate if todoist_project is defined when assignee_email is present

        Args:
            config_validate (dict): config to validate

        Raises:
            Exception: Raised if validation failed
        """
        for keep_list in config_validate['keep_lists']:
            keep_list_name = list(keep_list.keys())[0]
            keep_list_options = list(keep_list.values())[0]
            if self.parse_key(keep_list_options, 'assignee_email') and not self.parse_key(keep_list_options, 'todoist_project'):
                log.error(f'Validation failed for "{keep_list_name}" ❌')
                raise ConfigValidationError(f'Validation failed for "{keep_list_name}": lists with "assignee_email" have to define a shared "todoist_project"')
    
    @property
    def config(self):
        """Get config

        Returns:
            dict: deserialized config.yaml
        """
        return self._config
    
    @staticmethod
    def parse_key(keep_list: dict, key: str):
        return keep_list[key] if key in keep_list else None

class ConfigValidationError(Exception):
    pass