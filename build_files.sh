#!/bin/bash
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build completed." 