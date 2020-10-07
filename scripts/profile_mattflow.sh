#!bin/bash


cd ..
export PYTHONPATH="${PYTHONPATH}:${PWD}/mattflow"
kernprof -lv mattflow/__main__.py
cd scripts
