#! /bin/bash
set -x -o errexit

#curl  -d '{"s3_bucket":"spot.bot.asset", "s3_path":"train","bot_name":"CAR_ACCIDENT_INSPECTOR", "number_of_bots":"5","bulk_size":"500", "output_s3_bucket":"spot.bot.asset"}' -X POST 'https://x0p89jjuid.execute-api.us-east-1.amazonaws.com/Prod/create/proxy'
curl  -d '{"s3_bucket":"spot.bot.asset", "s3_path":"sentiment","bot_name":"SENTIMENT_ANALYSIS", "number_of_bots":"5","bulk_size":"500", "output_s3_bucket":"spot.bot.asset"}' -X POST 'https://x0p89jjuid.execute-api.us-east-1.amazonaws.com/Prod/create/proxy'

