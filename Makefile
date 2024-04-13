# Makefile to gather common commands

.PHONY: clean dcomp-up-data-feed dcomp-up-data-output d-down kafka-create-topic kafka-list-all-topics kafka-list-topic-msgs kafka-send-topic-msg pipenv-dev-install
.DEFAULT_GOAL := help

# Project variables
MODULE:=mypackage
SRC:=src/$(MODULE)

# Command overrides
# In docker-related commands, provide DOCKER=podman to use podman instead of docker
DOCKER:=docker

# Fetch from git tags the current dev version string, if not found use seconds since epoch
TAG := $(shell git describe --tags --always --dirty --broken 2>/dev/null || date +%s)

help: # Show this help menu
	$(info Available make commands:)
	@grep -e '^[a-z|_|-]*:.* ##' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS=":.* ## "}; {printf "\t%-23s %s\n", $$1, $$2};'

.print-phony:
	@echo "\n.PHONY: "
	@grep -e '^[a-z|_|-]*:.* ##' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS=":.* ## "}; {printf "%s ", $$1};'
	@echo "\n"

####### COMMANDS - META #######################################################################

clean: ## Clean up auxiliary and temporary files from the workspace
	$(info Cleaning auxiliary and temporary files...)
	@find . -maxdepth 1 -type d -name '.mypy_cache' -exec rm -r {} +
	@find . -maxdepth 1 -type d -name '.ruff_cache' -exec rm -r {} +
	@find . -maxdepth 1 -type d -name 'build'       -exec rm -r {} +
	@find . -maxdepth 1 -type d -name 'dist'        -exec rm -r {} +
	@find . -maxdepth 2 -type d -name '*.egg-info'  -exec rm -r {} +
	@echo Done.

pipenv-dev-install: ## Create dev venv
	@pipenv run pip install --upgrade pip
	@pipenv install --dev --ignore-pipfile --deploy

####### COMMANDS - MAIN #######################################################################

dcomp-up-deps: ## Start all dependencie services
	@docker-compose -p dep up -d --force-recreate --build

dcomp-up-data-feed: ## Start the data_feed service
	@docker-compose -p data_feed up -d --force-recreate --build

dcomp-up-data-output: ## Start the data_output services
	@docker-compose -p data_output up -d

d-down: ## Stop all services
	@ddocker-compose stop -t 0

####### COMMANDS - UTILITIES #######################################################################

kafka-create-topic: ## Create a "financial-transaction" topic directly in Kafka service
	@docker exec aml_kafka \
		/opt/kafka/bin/kafka-topics.sh \
		--bootstrap-server localhost:9092 \
		--create --topic financial-transaction \
		--partitions 1 \
		--replication-factor 1

kafka-list-all-topics: ## List all created topics in Kafka service
	@docker exec aml_kafka \
		/opt/kafka/bin/kafka-topics.sh \
		--bootstrap-server localhost:9092 \
		--list

kafka-list-topic-msgs: ## List all messages broadcasted to "financial-transaction" topic in Kafka service
	@docker exec aml_kafka \
		/opt/kafka/bin/kafka-console-consumer.sh \
		--bootstrap-server localhost:9092 \
		--topic financial-transaction \
		--from-beginning

kafka-send-topic-msg: ## Send a message to "financial-transaction" topic directly in Kafka service
	@echo "foo" |
		docker exec -i aml_kafka \
			/opt/kafka/bin/kafka-console-producer.sh \
			--broker-list localhost:9092 \
			--topic financial-transaction \
			-
