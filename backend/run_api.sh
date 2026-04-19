#!/bin/bash
# Script para rodar o backend FastAPI localmente fora do devcontainer/docker
# Uso: ./run_api.sh

cd "$(dirname "$0")" # vai para a pasta backend
export PYTHONPATH=src
uvicorn api.main:app --reload
