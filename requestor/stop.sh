#   Stop the server gracefully.
#   The best way to ensure graceful yapapi shutdown is to send SIGTERM (15) 
#   to the main gunicorn process and this is not obvious at all, thus this script.
#   (check e.g. https://github.com/benoitc/gunicorn/issues/2604)

#   NOTE: we can't use the standard `docker stop ...` because gunicorn is not the
#   "main" container process - the main process is yagna_and_server_init.sh.
GUNICORN_MASTER_PID=$(ps -aux | grep gunicorn | tr -s ' ' | cut -d ' ' -f2 | sort -n | head -1)
kill -15 $GUNICORN_MASTER_PID
