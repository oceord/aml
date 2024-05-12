# Roadmap

- [x] Overview Documentation
  - [x] README
  - [x] Diagram
- [ ] Setup
  - [x] Kafka
  - [x] Hadoop
  - [x] PostgreSQL
  - [ ] Spark
- [x] Kafka feed
  - [x] Stream data from the [IBM Transactions for AML](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) dataset
- [ ] Data ingestion through Spark
  - [x] Extract from Kafka stream
  - [x] Load raw data to Hadoop
  - [x] Transform and Load Fact tables to PostgreSQL
  - [ ] Validate data with Great Expectations
- [ ] Money laundering detection
  - [ ] [Realistic Synthetic Financial Transactions for Anti-Money Laundering Models](https://arxiv.org/pdf/2306.16424.pdf)
  - [ ] [Provably Powerful Graph Neural Networks for Directed Multigraphs](https://arxiv.org/pdf/2306.11586.pdf)
  - [ ] Detect money laundering through [Multi-GNN](https://github.com/IBM/Multi-GNN)
- [ ] Real-time money laundering detection

## Playground

- [ ] Use a Spark cluster to process data
- [ ] Apply MapReduce with Hadoop
  - [x] Total inbound transaction money by account
  - [x] Total outbound transaction money by account
  - [x] Total inbound transaction money by bank
  - [x] Total outbound transaction money by bank
