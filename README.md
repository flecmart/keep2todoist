# keep2todoist

Transfer items from google keep lists to todoist.

My use case is having an intuitive google assistant integration for todoist:

1. Sync your google notes and lists with google keep (setting in google assistant)
2. Let this tool move items from google keep lists to todoist lists.

It is not a real sync but just a **one way** keep->todoist.

- Moved items will be deleted from keep's list
- Labels on google keep lists will be attached to their corresponding todo tasks

This works also with archived google keep lists (in case you don't want your intermediate lists to distract you if you're actually using google keep).

## Configuration

Create a `config.yaml` from `config.example.yaml`:

```yaml
update_interval_s: 60
google_username: yourUsername
google_password: canBeAnAppPassword
todoist_api_token: todoistApiKey
keep_lists:  # list your keep lists on this level
  - Todo:
      sync_labels: false # required: transfer labels from gkeep lists to todoist items
      due_str_en: 'today' # optional: you can set a due date in english here
      # if todoist_project is not set your task will go into the todoist inbox
  - Shopping:
      sync_labels: false
      todoist_project: 'Shopping' # optional: you can choose a project for todoist here
  - Test:
      sync_labels: false
```

- It is recommended that you don't use your google main credentials.
Instead go to https://myaccount.google.com/apppasswords and generate an app password specifically for this tool
- Your todoist token can be found in todoist settings->integrations
- Changes of `config.yaml` will be detected automatically and the updated config will be reflected if the yaml is valid

## Start

Either use docker/docker-compose to start the service:

```bash
docker-compose up -d
```

or go to the app folder, install requirements and run the code directly:

```bash
cd app
pip install -r requirements.txt
python3 app.py
```

docker-compose has the advantage that the service will be restarted automatically on reboot or error.
