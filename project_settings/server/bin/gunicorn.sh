#!/bin/bash
echo "========================Working till here 1========================"
NAME="backend"                          # Name of the application
DJANGODIR=/opt/main_backend/mainbackend/       # Django project directory
SOCKFILE=/opt/main_backend/mainbackend/project_settings/server/bin/gunicorn.sock    # we will communicte using this unix socket
USER=dev-django1                                    # the user to run as
GROUP=webapps                                   # the group to run as
NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn
NUM_THREAD_PER_WORKERS=2                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=backend.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=backend.wsgi                     # WSGI module name
TIMEOUT=120 #https://stackoverflow.com/questions/6816215/gunicorn-nginx-timeout-problem
echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR

#add virtualenvwrapper related commands. Below $Home doesnt work as in the original
#scrypt as I think $HOME is still su
# export WORKON_HOME=~/.virtualenvs
#source /usr/local/bin/virtualenvwrapper_lazy.sh
#activate enviornment
#workon logic_srv
echo "========================Working till here========================"
source /home/dev-django1/.virtualenvs/logic_srv/bin/activate
#source ../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
#test if RUNDIR is present else make it
test -d $RUNDIR || mkdir -p $RUNDIR

# exec celery first
#exec celery_restart
#exec celerybeat_restart
#exec celerycam_restart


# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
echo "========================Working till here 7========================"
#exec gunicorn ${DJANGO_WSGI_MODULE}:application 127.0.0.1:8000\
#  --timeout $TIMEOUT \
#  --log-file=/opt/tmq_django/logs/gunicorn.log
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  -k=gevent \
  --workers $NUM_WORKERS \
  -k gevent \
  --threads $NUM_THREAD_PER_WORKERS \
  --timeout $TIMEOUT \
  --user=$USER \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=/opt/main_backend/logs/gunicorn.log \
  --max-requests 100 \
  --max-requests-jitter 20
echo f"========================Working till here 8 End=={NAME}======================"