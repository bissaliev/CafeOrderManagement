#!/bin/bash
sleep 2
python3 manage.py migrate
python3 manage.py collectstatic --no-input
python3 manage.py loaddata fixtures/dishes.json
python3 manage.py loaddata fixtures/orders.json
python3 manage.py loaddata fixtures/order_items.json
exec gunicorn --bind 0:8000 cafe.wsgi