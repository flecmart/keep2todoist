import yaml
import logging
import schedule
import time
import gkeepapi
from todoist_api_python.api import TodoistAPI

def load_configuration():
    try:
        with open('config.yaml', 'r') as yamlfile:
            config = yaml.safe_load(yamlfile)
    except Exception as ex:
        logging.error(f'Could not load configuration: {ex}')
    return config


def get_todoist_project_id(api, name):
    for project in todoist_api.get_projects():
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
            
            logging.info(f'\t-> {item.text}')
            item.delete()
    
    
def update():
    for keep_list in config['keep_lists']:
        keep_list_name = list(keep_list.keys())[0]
        logging.info(f'Transfering {keep_list_name} list from keep to todoist...')
        transfer_list(keep_list_name, parse_key(keep_list, 'todoist_project'), parse_key(keep_list, 'due_str_en'))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Loading configuration...')
    config = load_configuration()

    keep = gkeepapi.Keep()
    keep.login(config['google_username'], config['google_password'])
    
    todoist_api = TodoistAPI(config['todoist_api_token'])
    
    update_interval_s = config['update_interval_s']
    schedule.every(update_interval_s).seconds.do(update)
    
    logging.info('Start scheduler...')
    schedule.run_all()
    
    while True:
        schedule.run_pending()
        time.sleep(1)