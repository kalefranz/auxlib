#!/bin/bash -eu

cd "${1:-.}"
find . -name "*.pyc" -delete
