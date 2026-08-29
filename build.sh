#!/usr/bin/env bash
set -o errexit

python configuration/manage.py collectstatic --no-input
python configuration/manage.py migrate