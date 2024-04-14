# Makefile to gather common commands

.PHONY: clean dcomp-down dcomp-up-data-feed dcomp-up-data-output dcomp-up-deps d-exec-modify-hdfs-permissions hdfs-cat-raw-json hdfs-ls-raw-json hdfs-rm-aml kafka-create-topic kafka-list-all-topics kafka-list-topic-msgs kafka-send-topic-msg pipenv-dev-install
.DEFAULT_GOAL := help

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

dcomp-up-deps: ## Start all dependency services
	@docker-compose --profile dep up -d --force-recreate --build
	@make d-fix-hdfs-permissions

dcomp-up-data-feed: ## Start the data_feed service
	@docker-compose --profile data_feed up -d --force-recreate --build

dcomp-up-data-output: ## Start data_output services
	@docker-compose --profile data_output up -d
	@make d-fix-hdfs-permissions

d-fix-hdfs-permissions: ## Change permission of HDFS to allow anyone to write to it
	@docker exec aml_hadoop_namenode hadoop fs -chmod -R 777 /

dcomp-down: ## Stop all services
	@docker-compose stop -t 0

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

hdfs-ls-raw-json: ## List files in hdfs://localhost/aml/raw/events/json
	@docker exec aml_hadoop_datanode hdfs dfs -ls /aml/raw/events/json

hdfs-cat-raw-json: ## Cat json files in hdfs://localhost/aml/raw/events/json
	@docker exec aml_hadoop_datanode \
		hdfs dfs -cat \
		$$(docker exec aml_hadoop_datanode hdfs dfs -ls /aml/raw/events/json | grep '\.json$$' | awk '{print $$8}')

hdfs-rm-aml: ## Remote hdfs://localhost/aml directory
	@hdfs dfs -rm -r -f /aml
