##


## Local development

### Install poetry

```bash
$ pip3 install poetry
```

### Install Dependencies

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate          
$ poetry install
```

### Run Tests & checks

```bash
$ make test-all
```

### Run Local Server

```bash
$ export DJANGO_SETTINGS_MODULE=adm_portal.settings.dev
$ cd adm_portal
$ python manage.py runserver
```

