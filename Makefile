.PHONY: default format test-all docker-build docker-run docker-stop

default: format test-all

format:
	@ isort -rc adm_portal
	@ black adm_portal

test-all:
	@ isort -rc adm_portal --check-only
	@ black adm_portal --check --quiet
	@ flake8 adm_portal
	@ mypy adm_portal
	@ cd adm_portal && python manage.py makemigrations --check --dry-run && cd ..
	@ cd adm_portal && python manage.py test --exclude-tag=integration && cd ..

docker-build:
	@ echo "Building docker image"
	@ docker image build -t adm-portal .

docker-run:
	@ echo "Running docker image"
	@ docker container run -d -p 8000:8000 --name adm-portal-dev -e DJANGO_SETTINGS_MODULE -e SECRET_KEY -e AUTH_TOKEN -e ELASTICEMAIL_API_KEY adm-portal

docker-stop:
	@ echo "Stopping docker image"
	@ docker stop adm-portal-dev
	@ docker rm adm-portal-dev
