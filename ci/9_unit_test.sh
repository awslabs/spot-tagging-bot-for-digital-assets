#! /bin/bash
set -x
AWS_XRAY_CONTEXT_MISSING=LOG_ERROR pipenv run python -m pytest tests/ -v -s
