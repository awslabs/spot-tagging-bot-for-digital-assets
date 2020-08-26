#! /bin/bash
set -x -o errexit

curl -d '{"s3_bucket":"spot.bot.asset", "s3_path":"train","bot_name":"CAR_ACCIDENT_INSPECTOR","number_of_bots":"5","bulk_size":"500"}' \
     -X POST 'http://127.0.0.1:3000/Prod/create/proxy'
