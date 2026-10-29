#!/usr/bin/env bash
# Сборка приложения на хостинге Render (Build Command: bash build.sh)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_products
