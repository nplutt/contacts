#!/bin/bash

set -e

# Deploy and wait for the stack to build
aws cloudformation delete-stack --stack-name contacts-nplutt-bucket
aws cloudformation wait stack-delete-complete --stack-name contacts-nplutt-bucket
