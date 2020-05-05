#!/bin/bash
set -Eeuo pipefail
set -x

# Log in
http \
  --session=./session.json \
  --form POST \
  "http://localhost:8000/accounts/login/" \
  username=awdeorio \
  password=password \
  submit=login

# REST API request
http \
  --session=./session.json \
  "http://localhost:8000/api/v1/p/1/likes/"