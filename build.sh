#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

python manage.py makemigrations
# Apply any outstanding database migrations
python manage.py migrate
python manage.py shell << END
from django.contrib.auth import get_user_model

User = get_user_model()
username = "adiel"
email = "adiel@gmail.com"
password = "adiel"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created.")
else:
    print("Superuser already exists.")
END
