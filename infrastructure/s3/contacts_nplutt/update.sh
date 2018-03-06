#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
export PYTHONPATH=$PYTHONPATH:$(git rev-parse --show-toplevel)/infrastructure

# Create the cloudformation json file
python bucket.py

# Deploy and wait for the stack to build
aws cloudformation update-stack --stack-name contacts-nplutt-bucket --template-body file://$DIR/artifacts_bucket.json
aws cloudformation wait stack-update-complete --stack-name contacts-nplutt-bucket
