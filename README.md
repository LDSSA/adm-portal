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


### `ldssa-adm-portal`bucket structure

```
├── coding_test.ipynb
├── applications
│   ├── coding_test
│   |   └── user_1
|   │       ├── file_1
|   │       └── file_2
│   ├── slu01
│   |   └── user_1
|   │       └── file_1
│   ├── slu02
│   |   ├── user_1
|   │   |   ├── file_1
|   │   |   ├── file_2
|   │   |   └── file_3
│   |   └── user_2
|   │       └── file_1
│   └── slu03
│       └── user_1
|           └── file_1
└── payments
    ├── payment_proof
    │   ├── user_1
    │   |   ├── file_1
    |   |   └── file_2
    |   └── user_2
    │       └── file_1
    └── student_id
        └── user_1
            └── file_1
```
