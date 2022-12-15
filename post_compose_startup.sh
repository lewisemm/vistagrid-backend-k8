docker exec image_service python manage.py migrate

docker exec user_service flask db upgrade
