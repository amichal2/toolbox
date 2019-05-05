#!/bin/bash

set -e
set -o pipefail

ENV_NAME="venv"

~/homebrew/bin/python3 -m venv ${ENV_NAME}

${ENV_NAME}/bin/pip3 install --upgrade pip
${ENV_NAME}/bin/pip3 install -r requirements.txt

${ENV_NAME}/bin/python3 cf_restarts.py
