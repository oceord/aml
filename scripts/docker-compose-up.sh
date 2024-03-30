#!/usr/bin/env bash

docker-compose --profile dep --profile aml up -d --force-recreate --build
