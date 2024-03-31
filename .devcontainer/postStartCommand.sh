#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

pipenv run pip install --upgrade pip
pipenv install --dev --ignore-pipfile --deploy
