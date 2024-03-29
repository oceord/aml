# Real-Time Ingestion and Analysis of Financial Transactions

## Overview

This project aims to build a comprehensive data pipeline for real-time ingestion and analysis of financial transactions, focusing on expanding knowledge in Kafka, Hadoop, Great Expectations, Spark, and Machine Learning.
The pipeline will ingest data from a Kaggle dataset, process it through a series of technologies, and output the results to a PostgreSQL data warehouse, Hadoop for raw and formatted data storage, and apply machine learning models for money laundering detection.

[ROADMAP](ROADMAP.md)

## Project Components

### Data Source

- **Kaggle Dataset**: [IBM Transactions for AML](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)
- **Format**: CSV

### Data Feed

- **Kafka**: Used for real-time data streaming.

### Data Ingestion

- **Spark**: Utilized for processing and analyzing the data in real-time.

### Data Output

- **Hadoop**: Used for storing raw and formatted data.
- **PostgreSQL**: Serves as the data warehouse for storing processed and analyzed data.

### Data Validation

- **Great Expectations**: Ensures data quality and integrity through automated testing.

### Money Laundering Detection

- **[IBM/Multi-GNN](https://github.com/IBM/Multi-GNN)**: Machine learning models for detecting patterns indicative of money laundering activities.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
