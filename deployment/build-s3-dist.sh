#!/bin/bash
set -v
set -e
#
# This script should be run from the repo's deployment directory
# cd deployment
# ./build-s3-dist.sh template-bucket-name source-bucket-base-name solution-name version-code
#
# Parameters:
#  - template-bucket-name: Name for S3 bucket location where the template will be located in.
#
#  - source-bucket-base-name: Name for the S3 bucket location where the template will source the Lambda
#    code from. The template will append '-[region_name]' to this bucket name.
#    For example: ./build-s3-dist.sh solutions-reference solutions my-solution v1.0.0
#    The template will then expect the source code to be located in the solutions-[region_name] bucket
#
#  - solution-name: name of the solution for consistency
#
#  - version-code: version of the package
#

# Check to see if input has been provided:
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "Please provide the base source bucket name, trademark approved solution name and version where the lambda code will eventually reside."
    echo "For example: ./build-s3-dist.sh solutions-reference solutions trademarked-solution-name v1.0.0 "
    exit 1
fi

# Get reference for all important folders
template_dir="$PWD"
template_dist_dir="$template_dir/global-s3-assets"
build_dist_dir="$template_dir/regional-s3-assets"
source_dir="$template_dir/../source"
build_dir="$template_dir/../build"

echo "------------------------------------------------------------------------------"
echo "[Init] Clean old dist, node_modules and bower_components folders"
echo "------------------------------------------------------------------------------"
echo "rm -rf $template_dist_dir"
rm -rf $template_dist_dir
echo "mkdir -p $template_dist_dir"
mkdir -p $template_dist_dir
echo "rm -rf $build_dist_dir"
rm -rf $build_dist_dir
echo "mkdir -p $build_dist_dir"
mkdir -p $build_dist_dir

echo "------------------------------------------------------------------------------"
echo "[Packing] Templates"
echo "------------------------------------------------------------------------------"
# echo "cp $template_dir/*.template $template_dist_dir/"
# cp $template_dir/*.template $template_dist_dir/
echo "copy yaml templates and rename"
cp $template_dir/*.yaml $template_dist_dir/
cd $template_dist_dir
# Rename all *.yaml to *.template
for f in *.yaml; do
    mv -- "$f" "${f%.yaml}.template"
done

cd ..
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Updating code source bucket in template with $1"

    replace="s/%%TEMPLATE_BUCKET_NAME%%/$1/g"
    echo "sed -i '' -e $replace $template_dist_dir/*.template"
    sed -i '' -e $replace $template_dist_dir/*.template

    replace="s/%%BUCKET_NAME%%/$2/g"
    echo "sed -i '' -e $replace $template_dist_dir/*.template"
    sed -i '' -e $replace $template_dist_dir/*.template

    replace="s/%%SOLUTION_NAME%%/$3/g"
    echo "sed -i '' -e $replace $template_dist_dir/*.template"
    sed -i '' -e $replace $template_dist_dir/*.template

    replace="s/%%VERSION%%/$4/g"
    echo "sed -i '' -e $replace $template_dist_dir/*.template"
    sed -i '' -e $replace $template_dist_dir/*.template

else
    echo "Updating code source bucket in template with $1"

    replace="s/%%TEMPLATE_BUCKET_NAME%%/$1/g"
    echo "sed -i -e $replace $template_dist_dir/*.template"
    sed -i -e $replace $template_dist_dir/*.template

    replace="s/%%BUCKET_NAME%%/$2/g"
    echo "sed -i -e $replace $template_dist_dir/*.template"
    sed -i -e $replace $template_dist_dir/*.template

    replace="s/%%SOLUTION_NAME%%/$3/g"
    echo "sed -i -e $replace $template_dist_dir/*.template"
    sed -i -e $replace $template_dist_dir/*.template

    replace="s/%%VERSION%%/$4/g"
    echo "sed -i -e $replace $template_dist_dir/*.template"
    sed -i -e $replace $template_dist_dir/*.template
fi


echo "------------------------------------------------------------------------------"
echo "[Rebuild] sam_spot_bot_create_job"
echo "------------------------------------------------------------------------------"
# build and copy console distribution files
echo ${source_dir}
cd ${source_dir}/sam_spot_bot_create_job
rm -rf ${build_dir}
region="cn-north-1"

if [[ $region =~ ^cn.* ]]
then
    pip install -r ${source_dir}/requirements.txt -t ${build_dir} -i https://opentuna.cn/pypi/web/simple
else
    pip install -r ${source_dir}/requirements.txt -t ${build_dir}
fi

# boto are provided by Lambda runtime already.
mkdir -p ${build_dir}/sam_spot_bot_create_job/
cp -R *.py ${build_dir}/sam_spot_bot_create_job/
cd ${build_dir}
zip -r9 sam_spot_bot_create_job.zip .
cp ${build_dir}/sam_spot_bot_create_job.zip $build_dist_dir/sam_spot_bot_create_job.zip
rm ${build_dir}/sam_spot_bot_create_job.zip


echo "------------------------------------------------------------------------------"
echo "[Rebuild] sam_spot_bot_api_receiver"
echo "------------------------------------------------------------------------------"
# build and copy console distribution files
echo ${source_dir}
cd ${source_dir}/sam_spot_bot_api_receiver
rm -r ${build_dir}
region="cn-north-1"

if [[ $region =~ ^cn.* ]]
then
    pip install -r ${source_dir}/requirements.txt -t ${build_dir} -i https://opentuna.cn/pypi/web/simple
else
    pip install -r ${source_dir}/requirements.txt -t ${build_dir}
fi

# boto are provided by Lambda runtime already.
mkdir -p ${build_dir}/sam_spot_bot_api_receiver/
cp -R *.py ${build_dir}/sam_spot_bot_api_receiver/
cd ${build_dir}
zip -r9 sam_spot_bot_api_receiver.zip .
cp ${build_dir}/sam_spot_bot_api_receiver.zip $build_dist_dir/sam_spot_bot_api_receiver.zip
rm ${build_dir}/sam_spot_bot_api_receiver.zip
