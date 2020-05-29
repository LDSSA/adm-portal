# Custom Settings

## Email Client

#### Local

The Local Email Client doesn't actually send emails, it just dumps data in to the local disk.
**DO NOT USE THIS IN PRODUCTION**

```python
EMAIL_CLIENT="LOCAL"
EMAIL_LOCAL_DIR = os.path.join(os.path.dirname(BASE_DIR), ".mailbox")
```

#### Elastic

The Elastic Email Client uses the elastic email api to send emails.
[Elastic API Docs](https://api.elasticemail.com/public/help)

```python
EMAIL_CLIENT = "ELASTIC"
ELASTIC_EMAIL_API_KEY = os.environ["ELASTIC_EMAIL_API_KEY"]
ELASTIC_EMAIL_SENDER = "sender@adm.org"
```

#### AWS SES (Backup)

```python
EMAIL_CLIENT = "AWS_SES"
AWS_SES_EMAIL_SENDER = "sender@adm.org"
```

## Storage

#### Local

The Local Storage Client saves files in the local disk and server them via http.
**DO NOT USE THIS IN PRODUCTION**

```python
STORAGE_CLIENT = "LOCAL"
STORAGE_LOCAL_DIR = os.path.join(os.path.dirname(BASE_DIR), ".storage")
```


#### S3

The S3 Storage Client uses AWS S3 to store and serve files.

```python
STORAGE_CLIENT = "S3"
STORAGE_BUCKET = "ldssa-adm-portal-601"
```


## Flags

#### Mock

The Mock Feature Flags Client is to be used on tests.
**DO NOT USE THIS IN PRODUCTION**

```python
FF_CLIENT = "MOCK"
```

#### DB 

Th DB Feature Flag Client uses the available database to store flag state.

```python
FF_CLIENT = "DB"
```


## Grader

#### Fake

The Fake Grader Client computes a random grade.
**DO NOT USE THIS IN PRODUCTION**

```python
GRADER_CLIENT = "FAKE"
```


#### Http

The Http Grader Client makes an http request go get the grade.

```python
GRADER_CLIENT = "HTTP"
GRADER_CLIENT_URL = os.environ["ADM_GRADER_URL"]
GRADER_CLIENT_AUTH_TOKEN = os.environ["ADM_GRADER_AUTH_TOKEN"]
```