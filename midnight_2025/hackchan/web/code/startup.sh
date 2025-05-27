head -c32 /dev/urandom > secret.key
gunicorn -w 4 --threads 4 -b :8000 app:app