#! /bin/bash
set -x
mkdir -p sam_spot_bot_create_job/build/sam_spot_bot_create_job/
mkdir -p sam_spot_bot_api_receiver/build/sam_spot_bot_api_receiver/
cp -R sam_spot_bot_create_job/*.py sam_spot_bot_create_job/build/sam_spot_bot_create_job/
cp -R sam_spot_bot_api_receiver/*.py sam_spot_bot_api_receiver/build/sam_spot_bot_api_receiver/
sam local start-api