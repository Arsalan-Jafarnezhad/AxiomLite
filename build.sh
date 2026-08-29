#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python configuration/manage.py collectstatic --no-input
python configuration/manage.py migrate