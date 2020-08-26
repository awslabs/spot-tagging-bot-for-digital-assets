#! /bin/bash
set -x -o errexit

aws cloudformation delete-stack \
    --stack-name spot-bot-execution-planner

