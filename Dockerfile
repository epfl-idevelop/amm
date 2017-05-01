FROM python:3.6

MAINTAINER IDEVELOP <personnel.idevelop@epfl.ch>

WORKDIR /opt/amm

COPY ./requirements ./requirements/
COPY ./bin ./bin/
COPY ./src ./src/
COPY ./nginx/nginx.conf /etc/nginx/conf.d/amm.conf

ARG MAJOR_RELEASE
ARG MINOR_RELEASE
ARG BUILD_NUMBER
ARG REQUIREMENTS_FILE

ENV \
    SECRET_KEY=dummy \
    TEST_CORRECT_PWD=dummy \
    TEST_WRONG_PWD=dummy \
    TEST_USERNAME=dummy \
    LDAP_BASE_DN=o=epfl,c=ch \
    LDAP_SERVER=scoldap.epfl.ch \
    LDAP_SERVER_FOR_SEARCH=ldap.epfl.ch \
    LDAP_USER_SEARCH_ATTR=uid \
    LDAP_USE_SSL=true \
    CACHE_REDIS_LOCATION=redis://redis:6379/1 \
    CACHE_REDIS_CLIENT_CLASS=django_redis.client.DefaultClient \
    RANCHER_ENVIRONMENT_ID=prod \
    DJANGO_HOST=localhost \
    DJANGO_WORKER_COUNT=2 \
    MAJOR_RELEASE=${MAJOR_RELEASE} \
    MINOR_RELEASE=${MINOR_RELEASE} \
    BUILD_NUMBER=${BUILD_NUMBER} \
    AMM_AUTHENTICATOR_CLASS=ldap \
    DJANGO_SETTINGS_MODULE=config.settings.local \
    AMM_MYSQL_DOMAIN=.example.com \
    DJANGO_DEBUG=False
    

RUN pip install --no-cache-dir -r ${REQUIREMENTS_FILE}
RUN python ./src/manage.py collectstatic --no-input

# NOTE : if we have an ENTRYPOINT here Pycharm docker-compose
# integration doesn't work

# CMD gunicorn --reload -w ${DJANGO_WORKER_COUNT} -b :8000 --chdir /opt/amm/src/ --access-logfile config.wsgi:application

VOLUME ["/opt/amm/", "/etc/nginx/conf.d/"]

ENTRYPOINT [ "bash" ]
CMD ["-c", "gunicorn --reload -w ${DJANGO_WORKER_COUNT} -b :8000 --chdir /opt/amm/src/ --access-logfile - config.wsgi:application" ]
