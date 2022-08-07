# keep2todoist

Transfer items from google keep lists to todoist.

My use case is having an intuitive google assistant integration for todoist:

1. Sync your google notes and lists with google keep (setting in google assistant)
2. Let this tool move items from google keep lists to todoist lists.

It is not a real sync but just a **one way** keep->todoist.
Moved items will be deleted from keep's list.

## Configuration

Create a `config.yaml` from `config.example.yaml`:

```yaml
update_interval_s: 60
google_username: yourUsername
google_password: canBeAnAppPassword
todoist_api_token: todoistApiKey
keep_lists:  # list your keep lists on this level
  - Todo:
    due_str_en: today # optional: you can set a due date in english here
  - 'Shopping'
    todoist_project: 'Shopping' # optional: you can choose a project for todoist here
```

It is recommended that you don't use your google main credentials. 
Instead go to https://myaccount.google.com/apppasswords and generate an app password specifically for this tool.

Your todoist token can be found in todoist settings->integrations.

## Start

Either use docker/docker-compose to start the service or go to the app folder, install requirements and run the code directly.
