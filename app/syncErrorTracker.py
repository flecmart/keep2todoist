import logging
log = logging.getLogger(__name__)

class SyncErrorTracker():
    def __init__(self, unhealthy_after: int = 5):
        """Tracks sync errors during runtime in memory

        Args:
            unhealthy_after (int, optional): Don't ping healthcheck if the same sync error happens n times. Defaults to 5.
        """
        self._errors = {}
        self._healthy = True
        self._unhealthy_after = unhealthy_after
        
    @property
    def healthy(self):
        """Is application healhty

        Returns:
            bool: health state
        """
        return self._healthy
        
    def _get_error_key(self, keep_list_name: str, item_name: str) -> str:
        return f'{keep_list_name}_{item_name}'
        
    def record_error(self, keep_list_name: str, item_name: str, exception: Exception):
        """Record sync error

        Args:
            keep_list_name (str): name of keep list to sync
            item_name (str): name of item to sync
            exception (Exception): ocurred exception
        """
        log.error(f'could not sync {item_name} from {keep_list_name}: {exception}')
        
        error_key = self._get_error_key(keep_list_name, item_name)
        if error_key not in self._errors:
            self._errors[error_key] = {'count': 1, 'exceptions': [exception]}
        else:
            self._errors[error_key]['count'] += 1
            self._errors[error_key]['exceptions'].append(exception)
            
        if self._errors[error_key]['count'] >= self._unhealthy_after and self._healthy:
            self._healthy = False
            log.error('Unhealthy sync state')
            
    def successful_sync(self, keep_list_name: str, item_name: str):
        error_key = self._get_error_key(keep_list_name, item_name)
        if error_key in self._errors:
            del self._errors[error_key]
            
        if all(error['count'] < self._unhealthy_after for error in self._errors.values()) and not self._healthy:
            self._healthy = True
            log.info('Sync state is healthy again')
        