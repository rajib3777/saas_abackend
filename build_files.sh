#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --settings=config.settings_prod

# Run migrations
python manage.py migrate --settings=config.settings_prod
