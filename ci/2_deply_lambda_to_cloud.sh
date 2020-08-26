#! /bin/bash
set -x -o errexit

mkdir -p sam_spot_bot_create_job/build/sam_spot_bot_create_job/
mkdir -p sam_spot_bot_api_receiver/build/sam_spot_bot_api_receiver/
cp -R sam_spot_bot_create_job/*.py sam_spot_bot_create_job/build/sam_spot_bot_create_job/
cp -R sam_spot_bot_api_receiver/*.py sam_spot_bot_api_receiver/build/sam_spot_bot_api_receiver/

# TODO make the following automatic.
# aws s3 mb s3://spotbot.cf.code

aws cloudformation package \
    --template-file template.yaml \
    --output-template-file packaged.yaml \
    --s3-bucket spotbot.cf.code

aws cloudformation deploy \
    --template-file packaged.yaml \
    --stack-name spot-bot-execution-planner \
    --capabilities CAPABILITY_IAM

aws cloudformation describe-stacks \
    --stack-name spot-bot-execution-planner \
    --query 'Stacks[].Outputs'