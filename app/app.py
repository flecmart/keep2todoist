import logging
import schedule
import time
import gkeepapi
import sys
from todoist_api_python.api import TodoistAPI
from configManager import ConfigManager

log = logging.getLogger('app')

def get_todoist_project_id(api: TodoistAPI, name):
    """Get todoist project id by name.

    Args:
        api (TodoistAPI): api
        name (str): project name

    Returns:
        int: project id
    """
    for project in api.get_projects():
        if project.name == name:
            return project.id
    return None


def get_labels_from_todoist(api: TodoistAPI):
    """Get existing labels from todoist.

    Args:
        api (TodoistAPI): api

    Returns:
        _type_: TODO
    """
    try:
        return api.get_labels()
    except Exception as ex:
        log.exception(ex)


def create_todoist_labels_if_necessary(labels: list, api: TodoistAPI):
    """Compare yaml labels to labels from todoist api and create new labels if necessary. 

    Args:
        labels (list): list of labels from yaml
        api (TodoistAPI): api

    Returns:
        list<int>: list of corresponding todoist label ids 
    """
    label_ids = []
    todoist_labels = get_labels_from_todoist(api)
    for i, label in enumerate(labels):
        for todoist_label in todoist_labels:
            if label == todoist_label.name:
                log.debug(f'found todoist label {label} with id {todoist_label.id}')
                label_ids.append(todoist_label.id)
        if len(label_ids) <= i:
            try:
                new_label = api.add_label(name=label)
                log.debug(f'created todoist label {label} with id {new_label.id}')
                label_ids.append(new_label.id)
            except Exception as ex:
                log.exception(ex)
    return label_ids


def parse_key(keep_list: dict, key: str):
    return keep_list[key] if key in keep_list else None
    

def transfer_list(keep_list_name: str, todoist_project: str, due: str, labels: list):
    keep.sync()
    for keep_list in (keep.find(func=lambda x: x.title == keep_list_name)):
        for item in keep_list.items:
            label_ids = []
            if labels:
                label_ids = create_todoist_labels_if_necessary(labels, todoist_api)
            if todoist_project:
                todoist_project_id = get_todoist_project_id(todoist_api, todoist_project)
                todoist_api.add_task(content=item.text, project_id=todoist_project_id, due_string=due, due_lang='en', label_ids=label_ids)
            else:
                todoist_api.add_task(content=item.text, due_string=due, due_lang='en', label_ids=label_ids)
            
            log.info(f'\t-> {item.text}')
            item.delete()
    keep.sync()

    
def update():
    if configManager.needs_update():
        configManager.update_configuration()
    for keep_list in configManager.config['keep_lists']:
        keep_list_name = list(keep_list.keys())[0]
        log.info(f'transfering {keep_list_name} list from keep to todoist')
        transfer_list(keep_list_name, parse_key(keep_list, 'todoist_project'), parse_key(keep_list, 'due_str_en'), parse_key(keep_list, 'labels'))


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
