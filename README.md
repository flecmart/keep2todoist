# keep2todoist

Transfer items from google keep lists to todoist.

My use case is having an intuitive google assistant integration for todoist:

1. Sync your google notes and lists with google keep (setting in google assistant)
2. Let this tool move items from google keep lists to todoist lists.

It is not a real sync but just a **one way** keep->todoist.

- Moved items will be deleted from keep's list
- Labels on google keep lists will be attached to their corresponding todo tasks

## Configuration

Create a `config.yaml` from `config.example.yaml`:

```yaml
update_interval_s: 60
google_username: yourUsername
google_token: oauthMasterToken
todoist_api_token: todoistApiKey
healthcheck: # optional: configure some kind of healtcheck endpoint providing service monitoring, e.g. https://healthchecks.io/
  url: https://hc-ping.com/someuuid
  period_min: 30
untitled_notes: # optional: move all untitled notes to todoist inbox
  add_label: 'Sync' # required: add label to todoist note
  due_str_en: 'today' # optional: you can set a due date in english here
keep_lists:  # list your keep lists on this level
  - Todo:
      sync_labels: false # required: transfer labels from gkeep lists to todoist items
      due_str_en: 'today' # optional: you can set a due date in english here
      # if todoist_project is not set your task will go into the todoist inbox
  - Shared:
      sync_labels: true
      assignee_email: 'name@domain.tld' # optional: the email of the person to be assigned, requires todoist_project to be a shared project.
      todoist_project: 'Chores' # not optional in this case, should be a shared project
  - Shopping:
      sync_labels: false
      todoist_project: 'Shopping' # optional: you can choose a project for todoist here
  - Test:
      sync_labels: false
```

- For obtaining the google_token follow [Get master token](#get-master-token)
- Your todoist token can be found in todoist settings->integrations.
- Changes in `config.yaml` will be detected automatically and the updated config will be reflected if the yaml is valid.
- optionally, for setting up a healthcheck to ensure that your service is running you can use a service like https://healthchecks.io/:

![image](https://user-images.githubusercontent.com/10167243/192765584-80b1866d-7483-4693-9912-5fa769cbe0c4.png)

If configured it will provide you with an url and the app will ping this url every `period_min` minutes. On the healtcheck's service side you configure a matching period & grace time. You can then get notified if a ping is missed, e.g. via mail.

### Get master token

1. Go to https://accounts.google.com/EmbeddedSetup
2. Press F12 to open debugger in browser and open Application tab
3. Log in with your google account and continue until you click on agree and the browser window keeps loading
4. Obtain the oauth token from the debugger
5. Run

```bash
docker run --rm -it --entrypoint /bin/sh python:3 -c 'pip install gpsoauth; python3 -c '\''print(__import__("gpsoauth").exchange_token(input("Email: "), input("OAuth Token: "), input("Android ID: ")))'\'
```

- Put in your google email, the obtained token and leave Android ID blank
- Copy out the token from the response
- Don't leak that token, it is a master token that can be used for authenticating your google account!

For more details on how to obtain the token read through https://github.com/rukins/gpsoauth-java/blob/b74ebca999d0f5bd38a2eafe3c0d50be552f6385/README.md#receiving-an-authentication-token

## Start

### docker

You can use docker/docker-compose to start the service:

```bash
docker-compose up -d
```

This has the advantage that the service will be restarted automatically on reboot or error.

### Pre-built docker image

Latest  docker image is also available at `ghcr.io/flecmart/keep2todoist:latest
`

```bash
docker run -v ./config.yaml:/app/config.yaml --restart always ghcr.io/flecmart/keep2todoist:latest
```

### Local python installation

Tested this only with `python >= 3.9`

```bash
cd app
pip install -r requirements.txt
python3 app.py
```

## Related projects

- Tool to improve the alexa integration for todoist: https://github.com/ChristianKuehnel/todoistautomation

## Thanks

This tool relies heavily on and would not be possible without:

- https://github.com/simon-weber/gpsoauth
- https://github.com/kiwiz/gkeepapi
- https://developer.todoist.com/guides/#developing-with-todoist
