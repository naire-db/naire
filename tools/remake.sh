#!/bin/bash
set -e
cd "$(dirname "$0")/.."

MYSQL="sudo mysql"
APPS="user form"

remake() {
    $MYSQL < tools/drop.sql
    rm -rf ./*/migrations
    python manage.py makemigrations $APPS
    python manage.py migrate
}

remake
