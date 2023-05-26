docker exec image_service python manage.py migrate

docker exec user_service flask db upgrade

docker exec image_service celery -A image_service worker -l INFO
