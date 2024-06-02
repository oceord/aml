# Makefile to gather common commands

.PHONY: clean dcomp-down dcomp-up-data-feed dcomp-up-data-output dcomp-up-deps d-exec-modify-hdfs-permissions hdfs-cat-raw-json hdfs-ls-raw-json hdfs-rm-aml kafka-create-topic kafka-list-all-topics kafka-list-topic-msgs kafka-send-topic-msg pipenv-dev-install
.DEFAULT_GOAL := help

help: # Show this help menu
	$(info Available make commands:)
	@grep -e '^[a-z|_|-]*:.* ##' $(MAKEFILE_LIST) |\
		sort |\
		awk 'BEGIN {FS=":.* ## "}; {printf "\t%-23s %s\n", $$1, $$2};'

.print-phony:
	@echo "\n.PHONY: "
	@grep -e '^[a-z|_|-]*:.* ##' $(MAKEFILE_LIST) |\
		sort |\
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
	@sleep 5
	@$(MAKE) d-fix-hdfs-permissions

dcomp-up-data-feed: ## Start the data_feed service
	@docker-compose --profile data_feed up -d --force-recreate --build

dcomp-up-data-output: ## Start data_output services
	@docker-compose --profile data_output up -d
	@sleep 5
	@$(MAKE) d-fix-hdfs-permissions

d-fix-hdfs-permissions: ## Change permission of HDFS to allow anyone to write to it
	@docker exec aml_hadoop_namenode hadoop fs -chmod -R 777 /

dcomp-stop-data-feed: ## Stop data feed
	@docker-compose stop data_feed kafka

dcomp-down: ## Stop all services
	@docker-compose stop -t 0

####### COMMANDS - UTILITIES - KAFKA #######################################################################

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
		--topic financial-transaction

kafka-send-topic-msg: ## Send a message to "financial-transaction" topic directly in Kafka service
	@echo "foo" |\
		docker exec -i aml_kafka \
			/opt/kafka/bin/kafka-console-producer.sh \
			--broker-list localhost:9092 \
			--topic financial-transaction \
			-

####### COMMANDS - UTILITIES - HDFS #######################################################################

hdfs-ls-raw-json: ## List files in hdfs://localhost/aml/raw/events/json
	@docker exec aml_hadoop_namenode hdfs dfs -ls -h /aml/raw/events/json

hdfs-cat-raw-json: ## Cat json files in hdfs://localhost/aml/raw/events/json
	@docker exec aml_hadoop_namenode \
		hdfs dfs -cat \
		$$(docker exec aml_hadoop_namenode hdfs dfs -ls /aml/raw/events/json | grep '\.json$$' | awk '{print $$8}')

hdfs-rm-aml: ## Remote hdfs://localhost/aml directory
	@hdfs dfs -rm -r -f /aml

####### COMMANDS - UTILITIES - HADOOP #######################################################################

hadoop-setup-python3: ## Copy scripts to hadoop
	@if [ -z "$(shell docker exec aml_hadoop_namenode command -v python3 2>/dev/null)" ]; then \
		docker exec aml_hadoop_namenode sudo yum check-update --assumeno || true; \
		docker exec aml_hadoop_namenode sudo yum install -y python3; \
		docker exec aml_hadoop_namenode sudo yum clean all; \
	fi
	@if [ -z "$(shell docker exec aml_hadoop_datanode command -v python3 2>/dev/null)" ]; then \
		docker exec aml_hadoop_datanode sudo yum check-update --assumeno || true; \
		docker exec aml_hadoop_datanode sudo yum install -y python3; \
		docker exec aml_hadoop_datanode sudo yum clean all; \
	fi
	@if [ -z "$(shell docker exec aml_hadoop_resourcemanager command -v python3 2>/dev/null)" ]; then \
		docker exec aml_hadoop_resourcemanager sudo yum check-update --assumeno || true; \
		docker exec aml_hadoop_resourcemanager sudo yum install -y python3; \
		docker exec aml_hadoop_resourcemanager sudo yum clean all; \
	fi
	@if [ -z "$(shell docker exec aml_hadoop_nodemanager command -v python3 2>/dev/null)" ]; then \
		docker exec aml_hadoop_nodemanager sudo yum check-update --assumeno || true; \
		docker exec aml_hadoop_nodemanager sudo yum install -y python3; \
		docker exec aml_hadoop_nodemanager sudo yum clean all; \
	fi

hadoop-copy-scripts: ## Copy scripts to hadoop
	@docker exec aml_hadoop_namenode sudo rm -rf /aml/scripts
	@docker exec aml_hadoop_namenode sudo mkdir -p /aml/scripts
	@docker cp ${HOME}/Dev/aml/src/playground/hadoop/. aml_hadoop_namenode:/aml/scripts

hadoop-test-account_total_in: ## Test hadoop job locally
	@cat data/hadoop_test_data/part.json |\
		src/playground/hadoop/account_total_in_map.py |\
		sort |\
		src/playground/hadoop/total_reduce.py

hadoop-test-account_total_out: ## Test hadoop job locally
	@cat data/hadoop_test_data/part.json |\
		src/playground/hadoop/account_total_out_map.py |\
		sort |\
		src/playground/hadoop/total_reduce.py

hadoop-test-bank_total_in: ## Test hadoop job locally
	@cat data/hadoop_test_data/part.json |\
		src/playground/hadoop/account_total_in_map.py |\
		sort |\
		src/playground/hadoop/total_reduce.py |\
		src/playground/hadoop/bank_total_map.py |\
		sort |\
		src/playground/hadoop/total_reduce.py

hadoop-test-bank_total_out: ## Test hadoop job locally
	@cat data/hadoop_test_data/part.json |\
		src/playground/hadoop/account_total_out_map.py |\
		sort |\
		src/playground/hadoop/total_reduce.py |\
		src/playground/hadoop/bank_total_map.py |\
		sort |\
		src/playground/hadoop/total_reduce.py

hadoop-submit-account_total_in: hadoop-setup-python3 hadoop-copy-scripts ## Submit account_total_in
	@docker exec aml_hadoop_namenode hdfs dfs -rm -f -r /aml/out/account_total_in
	@docker exec aml_hadoop_namenode mapred streaming -files /aml/scripts/account_total_in_map.py,/aml/scripts/total_reduce.py \
		-input /aml/raw/events/json \
		-output /aml/out/account_total_in \
		-mapper account_total_in_map.py \
		-reducer total_reduce.py

hdfs-cat-out-account_total_in: ## Echo output
	@docker exec aml_hadoop_namenode hdfs dfs -cat /aml/out/account_total_in/part-00000

hadoop-submit-account_total_out: hadoop-setup-python3 hadoop-copy-scripts ## Submit account_total_out
	@docker exec aml_hadoop_namenode hdfs dfs -rm -f -r /aml/out/account_total_out
	@docker exec aml_hadoop_namenode mapred streaming -files /aml/scripts/account_total_out_map.py,/aml/scripts/total_reduce.py \
		-input /aml/raw/events/json \
		-output /aml/out/account_total_out \
		-mapper account_total_out_map.py \
		-reducer total_reduce.py

hdfs-cat-out-account_total_out: ## Echo output
	@docker exec aml_hadoop_namenode hdfs dfs -cat /aml/out/account_total_out/part-00000

hadoop-submit-bank_total_in: hadoop-setup-python3 hadoop-copy-scripts ## Submit bank_total_in
	@docker exec aml_hadoop_namenode hdfs dfs -rm -f -r /aml/out/bank_total_in
	@docker exec aml_hadoop_namenode mapred streaming -files /aml/scripts/bank_total_map.py,/aml/scripts/total_reduce.py \
		-input /aml/out/account_total_in/part-00000 \
		-output /aml/out/bank_total_in \
		-mapper bank_total_map.py \
		-reducer total_reduce.py

hdfs-cat-out-bank_total_in: ## Echo output
	@docker exec aml_hadoop_namenode hdfs dfs -cat /aml/out/bank_total_in/part-00000

hadoop-submit-bank_total_out: hadoop-setup-python3 hadoop-copy-scripts ## Submit bank_total_out
	@docker exec aml_hadoop_namenode hdfs dfs -rm -f -r /aml/out/bank_total_out
	@docker exec aml_hadoop_namenode mapred streaming -files /aml/scripts/bank_total_map.py,/aml/scripts/total_reduce.py \
		-input /aml/out/account_total_out/part-00000 \
		-output /aml/out/bank_total_out \
		-mapper bank_total_map.py \
		-reducer total_reduce.py

hdfs-cat-out-bank_total_out: ## Echo output
	@docker exec aml_hadoop_namenode hdfs dfs -cat /aml/out/bank_total_out/part-00000
