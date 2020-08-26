#! /bin/bash
set -x

# the parameter should be --cloud-only for $1 if you want to include boto3 for local run - Like unit tiest.
# (boto3 is provided by Lambda runtime already)
proj_dir="$PWD"/..
src_dir="$proj_dir/src"
ut_dir="$proj_dir/tests/unit"

lambda_foldes="sam_spot_bot_create_job sam_spot_bot_get_job_status sam_spot_bot_api_receiver sam_spot_bot_function"

for l in $lambda_foldes; do
  rm -r "$src_dir/$l"/build/
done

# These are the implemented ones
lambda_foldes="sam_spot_bot_api_receiver sam_spot_bot_function"
create_job_folder="sam_spot_bot_create_job"

pip install -r "$proj_dir/requirements.txt" -t "$src_dir/$create_job_folder"/build/ -i https://pypi.tuna.tsinghua.edu.cn/simple
mkdir "$src_dir/$create_job_folder/build/$create_job_folder"/
cp -R "$src_dir/$create_job_folder"/*.py "$src_dir/$create_job_folder/build/$create_job_folder"/

cp -R "$src_dir/$create_job_folder"/build "$ut_dir"/build/

for l in $lambda_foldes; do
  # All functions share the same set of dependencies.
  cp -R "$src_dir/$create_job_folder"/build "$src_dir/$l"/build/
  mkdir "$src_dir/$l/build/$l"/
  mkdir "$ut_dir/build/$l"/
  cp -R "$src_dir/$l"/*.py "$src_dir/$l/build/$l"/
  cp -R "$src_dir/$l"/*.py "$ut_dir/build/$l"/
  # Move the requirements.txt to the folder of the lambda so it will be used by pipeline scripts at ../../deployment
  cat "$proj_dir/requirements.txt" | sed '/^boto3/d' >"$src_dir/$l"/requirements.txt
done
