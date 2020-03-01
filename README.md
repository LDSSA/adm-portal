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


### TODO list

- [ ] On the candidate navbar, the `Payment` tab should only show up if the candidate has a payment (i.e, passed the tests and was selected in the selection process). Need to add user_has_payments to all pages
- [x] First time we go to a Profile page for a new candidate, the page is ugly (no space betwen nav bar and header)
- [x] Remove banner "This test is ongoing" on the Coding test submissison page
- [ ] Email message is wrong
- [ ] We are still using dummy nbgrader notebooks
- [ ] Review Submission Types (min_score, repo, duration, etc..)
- [ ] Review "applications_close_at" datetime
- [ ] edge case: candidate starts test with only one hour until applications close. needs fix 
- [ ] fix staff applications view (super broken now)