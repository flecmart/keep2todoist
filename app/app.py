import logging
import schedule
import time
import gkeepapi
import sys
import os
from todoist_api_python.api import TodoistAPI
from configManager import ConfigManager
from syncErrorTracker import SyncErrorTracker
parse_key = ConfigManager.parse_key

log = logging.getLogger('app')
sync_errors = SyncErrorTracker()

def restart():
    log.info('restarting...')
    os.execv(sys.executable, ['python'] + sys.argv)
    
def google_login(keep: gkeepapi.Keep, user: str, password: str, device_id: str):
    """Authenticate gkeepapi. Try to use cached_token.

    Args:
        keep (gkeepapi.Keep): Keep object from gkeepapi
        user (str): google username
        password (str): google password, prefered one from https://security.google.com/settings/security/apppasswords
        device_id (str): device_id to use for authentication
    """
    log.info("authenticating gkeepapi")
    logged_in = False
    
    try:
        with open('gkeepapi_token', 'r') as cached_token:
            token = cached_token.read()
    except FileNotFoundError:
        token = None
    
    if token:
        try:
            keep.resume(user, token, sync=False, device_id=device_id)
            logged_in = True
            log.info("Successfully authenticated with token 👍")
        except gkeepapi.exception.LoginException:
            log.warning("invalid token ⚠️")
            
    if not logged_in:
        try:
            log.info('requesting new token')
            keep.login(user, password, sync=False, device_id=device_id)
            logged_in = True
            token = keep.getMasterToken()
            with open('gkeepapi_token', 'w') as cached_token:
                cached_token.write(token)
            log.info("authenticated successfully 👍")
        except gkeepapi.exception.LoginException as ex:
            log.info(f'failed to authenticate ❌ {ex}')
            sys.exit(1)
            
def ping_healthcheck(healthcheck_url: str):
    """Ping some kind of healthcheck url providing a possibility to monitor this service
    """
    import socket
    import urllib.request

    if sync_errors.healthy:
        try:
            log.info(f'ping {healthcheck_url}')
            urllib.request.urlopen(healthcheck_url, timeout=10)
        except socket.error as ex:
            log.warning(f'failed to ping {healthcheck_url}: {ex}')

def get_todoist_project_id(api: TodoistAPI, name):
    """Get todoist project id by name

    Args:
        api (TodoistAPI): api
        name (str): project name

    Returns:
        int: project id
    """
    try:
        for project in api.get_projects():
            if project.name == name:
                return project.id
    except Exception as ex:
        log.error(f'failed to get projects from todoist api: {ex}')
        return None

def get_labels_from_todoist(api: TodoistAPI):
    """Get existing labels from todoist

    Args:
        api (TodoistAPI): api

    Returns:
        list<Label>: list of todoist labels
    """
    try:
        return api.get_labels()
    except Exception as ex:
        log.error(f'failed to get labels from todoist api: {ex}')
        return []

def create_todoist_labels_if_necessary(labels: list, api: TodoistAPI):
    """Compare keep labels to labels from todoist api and create new labels if necessary

    Args:
        labels (list): list of labels
        api (TodoistAPI): api

    Returns:
        list<str>: list of corresponding todoist labels
    """
    labels_for_task = []
    todoist_labels = get_labels_from_todoist(api)
    for i, label in enumerate(labels):
        for todoist_label in todoist_labels:
            if label == todoist_label.name:
                log.debug(f'found todoist label {label} with id {todoist_label.id}')
                labels_for_task.append(todoist_label.name)
        if len(labels_for_task) <= i:
            new_label = api.add_label(name=label)
            log.debug(f'created todoist label {label} with id {new_label.id}')
            labels_for_task.append(new_label.name)
    return labels_for_task

def get_labels_on_gkeep_list(gkeep_list, gkeeplabels):
    """Get all labels on a gkeep list

    Args:
        gkeep_list (keepapi.node.List): Google keep list from gkeepapi
        gkeeplabels (list): List of gkeepapi.node.Label

    Returns:
        list: List of label names or None
    """
    labels_on_list = []
    for label in gkeeplabels:
        if gkeep_list.labels.get(label.id) != None:
            labels_on_list.append(label.name)
    if len(labels_on_list) == 0:
        return None
    log.info(f'list_labels on {gkeep_list.title}: {labels_on_list}')
    return labels_on_list

def get_assignee(api: TodoistAPI, project_id: str, email: str):
    if project_id and email:
        for collaborator in api.get_collaborators(project_id):
            if collaborator.email == email:
                return collaborator.id
    return None

def transfer_list(keep_list_name: str, todoist_project: str, due: str, sync_labels: bool, assignee_email: str):
    keep.sync()
    all_labels = keep.labels() if sync_labels else None
    for keep_list in (keep.find(func=lambda x: x.title == keep_list_name)):
        labels = get_labels_on_gkeep_list(keep_list, all_labels) if sync_labels else None
        for item in keep_list.items:
            try:
                task_added = None
                todoist_labels = []
                if labels:
                    todoist_labels = create_todoist_labels_if_necessary(labels, todoist_api)
                if todoist_project:
                    todoist_project_id = get_todoist_project_id(todoist_api, todoist_project)
                    assignee = get_assignee(todoist_api, todoist_project_id, assignee_email)
                    task_added = todoist_api.add_task(content=item.text, project_id=todoist_project_id, due_string=due, due_lang='en', labels=todoist_labels, assignee_id=assignee)
                else:
                    task_added = todoist_api.add_task(content=item.text, due_string=due, due_lang='en', labels=todoist_labels)
            except Exception as ex:
                sync_errors.record_error(keep_list_name, item.text, ex)

            if task_added:
                try:
                    item.delete()
                except Exception as ex:
                    sync_errors.record_error(keep_list_name, item.text, ex)
                    todoist_api.delete_task(task_added.id)
                    
            sync_errors.successful_sync(keep_list_name, item.text)
            log.info(f'\t-> {item.text}')
    keep.sync()

def transfer_untitled_notes(add_label: str, due: str):
    keep.sync()
    todoist_labels = []
    if add_label:
        labels = [add_label]
        todoist_labels = create_todoist_labels_if_necessary(labels, todoist_api)
    for untitled_note in keep.find(func=lambda x: x.title == ''):
        log.info(f'transfering untitled note from keep to todoist:')
        task_added = None
        try:
            task_added = todoist_api.add_task(content=untitled_note.text, due_string=due, due_lang='en', labels=todoist_labels)
        except Exception as ex:
            sync_errors.record_error('untitled', untitled_note, ex)
        
        if task_added:
            try:
                untitled_note.trash()
            except Exception as ex:
                sync_errors.record_error('untitled', untitled_note, ex)
                todoist_api.delete_task(task_added.id)
        
        sync_errors.successful_sync('untitled', untitled_note)
        log.info(f'\t-> {untitled_note.text}')
    keep.sync()

def update():
    if configManager.needs_update():
        configManager.update_configuration()
        restart()
    for keep_list in configManager.config['keep_lists']:
        keep_list_name = list(keep_list.keys())[0]
        keep_list_options = list(keep_list.values())[0]
        log.info(f'transfering {keep_list_name} list from keep to todoist')
        transfer_list(keep_list_name,
                      parse_key(keep_list_options, 'todoist_project'),
                      parse_key(keep_list_options, 'due_str_en'),
                      parse_key(keep_list_options, 'sync_labels'),
                      parse_key(keep_list_options, 'assignee_email'))
    if 'untitled_notes' in  configManager.config.keys():
        untitled_notes_options = configManager.config['untitled_notes']
        transfer_untitled_notes(parse_key(untitled_notes_options, 'add_label'), parse_key(untitled_notes_options, 'due_str_en'))

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(asctime)s %(name)s-%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    configManager = ConfigManager('config.schema.yaml', 'config.yaml')

    keep = gkeepapi.Keep()
    google_login(keep, configManager.config['google_username'], configManager.config['google_password'], device_id='3ee9002270d00157')

    todoist_api = TodoistAPI(configManager.config['todoist_api_token'])

    update_interval_s = configManager.config['update_interval_s']
    schedule.every(update_interval_s).seconds.do(update)

    log.info('start scheduler')
    update()
    
    if 'healthcheck' in configManager.config.keys():
        healthcheck_url = configManager.config['healthcheck']['url']
        healtheck_period_min = configManager.config['healthcheck']['period_min']
        ping_healthcheck(healthcheck_url)
        schedule.every(healtheck_period_min).minutes.do(ping_healthcheck, healthcheck_url=healthcheck_url)

    while True:
        schedule.run_pending()
        time.sleep(1)
