# Admissions Portal

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


### `ldssa-adm-portal-601`bucket structure

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


## Deployment Details Summary

### Requirements

##### AWS RDS Instance (PostgreSQL)

- DB details (host, port, user, pw) are taken from the environment
- It would be nice to be able to query the database without going through the service


##### AWS S3 Bucket 

- Read permission required
- Write permission required
- Bucket name is taken from the environment


### Django Commands

These must be ran on the instance.

Create Admin User:
```bash
$ cd app/adm_portal
$ python manage.py create_admin --email admin@lisbondatascience.org --password 
```

Create Staff User:
```bash
$ cd app/adm_portal
$ python manage.py create_staff --email staff@lisbondatascience.org --password 
```


### Docker Image

[DockerFile](./Dockerfile)

(Currently using `python3.8-buster` instead of `python3.8-alpine` because of postgresql dependency `psycopg2`)

[ci](./.github/workflows/ci_cd.yml) 

Building and Pushing new docker image on green commits on master 

[@dockerhub](`https://hub.docker.com/r/acci/adm-portal/tags`)


### Production ENV

- `DJANGO_SETTINGS_MODULE`: `adm_portal.settings.prod`

- `DJANGO_SECRET_KEY`: secret, can be generated

- `POSTGRES_NAME`: dependent on the created `AWS RDS` instance
- `POSTGRES_USER`: dependent on the created `AWS RDS` instance
- `POSTGRES_PASSWORD`: dependent on the created `AWS RDS` instance
- `POSTGRES_HOST`: dependent on the created `AWS RDS` instance
- `POSTGRES_PORT`: dependent on the created `AWS RDS` instance

- `ELASTIC_EMAIL_API_KEY`: provided by us
- `ELASTIC_EMAIL_SENDER`: provided by us

- `S3_BUCKET_NAME`: dependent on the created `S3 Bucket` name

- `ADM_GRADER_URL`: dependent on the AWS LAMBDA (for now it can be provided by us)
- `ADM_GRADER_AUTH_TOKEN`: secret, can be generated, needs to be consistent with the one on the AWS LAMBDA


### Nice to have / Later

- SSH access?
- logs on cloudwatch?
- take secrets (for example `ADM_GRADER_AUTH_TOKEN`) from AWS SECRETS MANAGER
- Deal with admin/staff creation on deploy (how to manage secrets?)
