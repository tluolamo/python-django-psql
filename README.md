# Readme

This API uses [Django Rest Framework](https://www.django-rest-framework.org/) for the basic REST API. With it you get browsable API which you can access by hitting the base URL with your browser.

It also uses [Celery](https://docs.celeryproject.org/en/stable/) to handle uploaded file processing asynchronously.

## Dev Environment

It is setup to use [SQLite3](https://www.sqlite.org/) for its main DB as well as for Celery.

To get up and running I recommend using virtual environment, specifically [pipenv](https://pypi.org/project/pipenv/) makes creating the environment easy.

### Setup instructions:
RHis was developed on Python 3.7 and it is part of the requirements, but should run on most any version of Python 3. If you are using version other than 3.7 then change the Pipfile `[requires]` section `python_version` to your version and delete the `Pipfile.lock` first 
Go into the project root folder, then run the following:

To create the environment:

    pipenv install --dev

Get into the environment

    pipenv shell

Run migrations:

    ./manage.py migrate`

If you want some sample data run this

    ./manage.py loaddata test_data

Start Celery:

    celery -A mp_apps worker -l info

Open a new shell and navigate to the project root folder, then execute the following to get django running:

    pipenv shell
    ./manage.py runserver

## Prod environment

For production you want to use something other than SQLite3 for the data storage. You can adjust the settings in the `mp_apps/settings.py` or provide your own alternative when starting the service.

You also need to make sure `DEBUG=False` and provide appropriate `ALLOWED_HOSTS` setting.

### DB
For the main DB good alternative would be [PostgreSQL](https://www.postgresql.org/) you can get a instance from [ElephantSQL](https://www.elephantsql.com/) as a service. To configure Django to use it instead you will settings file:

    DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'mydatabase',
          'USER': 'mydatabaseuser',
          'PASSWORD': 'mypassword',
          'HOST': '127.0.0.1',
          'PORT': '5432',
      }
    }

### Celery
For Celery a good backend production alternative would be [Redis](https://redis.io/). To reconfigure celery to use alternative backend change the following keys in the settings file

    CELERY_BROKER_URL
    CELERY_RESULT_BACKEND

For example Redis backend would look like:

    CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

More info on Redis configuration is available [here](https://docs.celeryproject.org/en/3.1/configuration.html#conf-redis-result-backend)

## Testing

To run the tests you can do

    ./manage.py test

To get coverage report you can do

    coverage run manage.py test; coverage report

## Example usage

List Members

    curl --location --request GET 'http://127.0.0.1:8000/members/'

Get member by id

    curl --location --request GET 'http://127.0.0.1:8000/members/1'

Get members by account id

    curl --location --request GET 'http://127.0.0.1:8000/members/?account_id=12'

Get members by phone number

    curl --location --request GET 'http://127.0.0.1:8000/members/?phone_number=1229470940'

Get members by client member id

    curl --location --request GET 'http://127.0.0.1:8000/members/?client_member_id=1289283'

You can also do combinations of the above filters

    curl --location --request GET 'http://127.0.0.1:8000/members/?account_id=5&phone_number=2642745297'

Create new member

    curl --location --request POST 'http://127.0.0.1:8000/members/' \
    --header 'Content-Type: application/json' \
    --data-raw '
    {
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": 8185551212,
    "client_member_id": 1,
    "account_id": 1
    }'

Upload a file

    curl --location --request POST 'http://127.0.0.1:8000/upload/new_member_data.csv' \
    --header 'Content-Type: text/csv' \
    --data-binary '@/path/to/my/file/new_member_data.csv'
