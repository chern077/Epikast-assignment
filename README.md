# DNS Log Analytics Pipeline – Deployment Guide

Here’s everything you need to replicate and test the DNS log pipeline I’ve built using AWS services. It ingests log files from S3, transforms them via Glue, stores the data in RDS PostgreSQL,
and serves aggregated log counts through a secure Lambda+API Gateway setup.

---

## Stack Overview

| Service       | Purpose                                      |
|---------------|----------------------------------------------|
| **S3**        | Raw log file source                          |
| **AWS Glue**  | ETL: Parses and loads log data into RDS      |
| **RDS PostgreSQL** | Stores structured DNS logs              |
| **Lambda (Docker)** | Queries log entry counts               |
| **API Gateway** | Exposes Lambda via secured HTTP API       |
| **CloudWatch** | Logs for Glue + Lambda                      |

---


### ✅ 1. Upload Log File to S3

- Upload `dns_log_file.txt` to a bucket, e.g., `s3://epikastdemo/`

---

### ✅ 2. Provision PostgreSQL RDS

- Launch PostgreSQL RDS in a private subnet
- DB name: `logdb`
- Create a table:

--sql
CREATE TABLE logs (
  log_time TIMESTAMP,
  geography TEXT,
  method TEXT,
  client_ip TEXT,
  url_request TEXT,
  query_type TEXT,
  query_flags TEXT
);
- Ensure port 5432 is allowed from Lambda's security group
### Loading DNS Logs into RDS

The logs are transformed and loaded into the `logs` table using a Glue job that parses the raw `.txt` file from S3. 

3. Run Glue Job

- Create a Glue job (Python shell or Spark job)
- Use PySpark to:
  - Read the `.txt` from S3
  - Parse DNS log lines using regex
  - Extract fields like `log_time`, `client_ip`, `url_request`, etc.
  - Write to the `logs` table in RDS

4. Build and Deploy Lambda (Docker-based)

- Clone the Lambda project and use public.ecr.aws/lambda/python:3.9 as the base image
- requirements.txt contains psycopg2-binary
- Handler: app.lambda_handler

Build and push:

docker build -t lambda-postgres .
docker tag lambda-postgres:latest <your-ecr-uri>:latest
docker push <your-ecr-uri>:latest

Configure environment variables:

DB_HOST      - RDS endpoint
DB_NAME      - logdb
DB_USER      - admin
DB_PASSWORD  - yourpassword
DB_PORT      - 5432

- Attach to the same VPC and subnet as the RDS
- Add a role with access to VPC, ECR, and CloudWatch

5. Add API Gateway in Front of Lambda

- Create a REST API via API Gateway
- Create resource `/logs` and POST method → integrate with Lambda
- Set “API Key Required” = true
- Deploy to a stage (e.g., prod)

6. Create API Key and Usage Plan

- Create an API key
- Create a Usage Plan and attach the API key
- Link it to your API stage

