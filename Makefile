.PHONY: default format test-all dev-fixtures dev-run docker-build docker-run docker-stop

CI_SETTINGS=adm_portal.settings.ci
DEV_SETTINGS=adm_portal.settings.dev

# development

default: format test-all

format:
	@ isort -rc adm_portal
	@ black adm_portal

test-all:
	@ isort -rc adm_portal --check-only
	@ black adm_portal --check --quiet
	@ flake8 adm_portal
	@ mypy adm_portal
	@ cd adm_portal && DJANGO_SETTINGS_MODULE=$(CI_SETTINGS) python manage.py makemigrations --check --dry-run && cd ..
	@ cd adm_portal && DJANGO_SETTINGS_MODULE=$(CI_SETTINGS) python manage.py test  --verbosity=0 --exclude-tag=integration && cd ..

dev-fixtures:
	@ cd adm_portal && rm -f adm_portal/db.sqlite3
	@ cd adm_portal && DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) python manage.py migrate
	@ cd adm_portal && DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) python manage.py generate_fixtures

dev-run:
	@ cd adm_portal && DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) python manage.py migrate
	@ cd adm_portal && DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) python manage.py runserver

loadtest:
	@locust -f loadtest.py -u 40 -r 4 --web-host 0.0.0.0 --web-port 8089

DOCKER_TAG=adm-portal
CONTAINER_NAME=adm-portal-dev

docker-build:
	@ echo "Building docker image"
	@ docker image build -t $(DOCKER_TAG) .

dev-run-docker: docker-build
	@ echo "Running docker container"
	@ DJANGO_SETTINGS_MODULE=$(DEV_SETTINGS) docker container run -d -p 8000:8000 --name $(CONTAINER_NAME) -e DJANGO_SETTINGS_MODULE $(DOCKER_TAG)

dev-kill-docker:
	@ echo "Killing docker container"
	@ docker stop $(CONTAINER_NAME)
	@ docker rm $(CONTAINER_NAME)

# AWS cloudformation

aws-deploy-s3:
	@ aws cloudformation deploy --template-file aws-cloudformation/s3.yaml --stack-name adm-portal-storage --no-fail-on-empty-changeset
	@ echo "Checking if required files exits"; aws s3api head-object --bucket ldssa-adm-portal-601 --key coding_test.ipynb > /dev/null 2>&1
