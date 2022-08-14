import logging
import schedule
import time
import gkeepapi
import sys
from todoist_api_python.api import TodoistAPI
from configManager import ConfigManager

log = logging.getLogger('app')

def get_todoist_project_id(api, name):
    for project in api.get_projects():
        if project.name == name:
            return project.id
    return None


def parse_key(keep_list: dict, key: str):
    return keep_list[key] if key in keep_list else None
    

def transfer_list(keep_list_name: str, todoist_project: str, due: str):
    keep.sync()
    for keep_list in (keep.find(func=lambda x: x.title == keep_list_name)):
        for item in keep_list.items:
            if todoist_project:
                todoist_project_id = get_todoist_project_id(todoist_api, todoist_project)
                todoist_api.add_task(content=item.text, project_id=todoist_project_id, due_string=due, due_lang='en')
            else:
                todoist_api.add_task(content=item.text, due_string=due, due_lang='en')
            
            log.info(f'\t-> {item.text}')
            item.delete()
    keep.sync()

    
def update():
    if configManager.needs_update():
        configManager.update_configuration()
    for keep_list in configManager.config['keep_lists']:
        keep_list_name = list(keep_list.keys())[0]
        log.info(f'transfering {keep_list_name} list from keep to todoist')
        transfer_list(keep_list_name, parse_key(keep_list, 'todoist_project'), parse_key(keep_list, 'due_str_en'))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(asctime)s %(name)s-%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    configManager = ConfigManager('config.yaml')
    
    keep = gkeepapi.Keep()
    keep.login(configManager.config['google_username'], configManager.config['google_password'])
    
    todoist_api = TodoistAPI(configManager.config['todoist_api_token'])
    
    update_interval_s = configManager.config['update_interval_s']
    schedule.every(update_interval_s).seconds.do(update)
    
    log.info('start scheduler')
    schedule.run_all()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
