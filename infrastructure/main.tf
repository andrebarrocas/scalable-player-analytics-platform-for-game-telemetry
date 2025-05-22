terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "game-analytics-vpc"
  }
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "game-analytics-public-${count.index + 1}"
  }
}

# Kinesis Streams
resource "aws_kinesis_stream" "game_events" {
  name             = "game-events-stream"
  shard_count      = 2
  retention_period = 24
  encryption_type  = "KMS"
  kms_key_id       = aws_kms_key.kinesis.id

  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes",
    "IncomingRecords",
    "OutgoingRecords"
  ]

  tags = {
    Environment = "production"
  }
}

resource "aws_kinesis_stream" "session_metrics" {
  name             = "session-metrics"
  shard_count      = 1
  retention_period = 24
  encryption_type  = "KMS"
  kms_key_id       = aws_kms_key.kinesis.id

  tags = {
    Environment = "production"
  }
}

resource "aws_kinesis_stream" "revenue_metrics" {
  name             = "revenue-metrics"
  shard_count      = 1
  retention_period = 24
  encryption_type  = "KMS"
  kms_key_id       = aws_kms_key.kinesis.id

  tags = {
    Environment = "production"
  }
}

# S3 Buckets
resource "aws_s3_bucket" "raw_data" {
  bucket = "game-analytics-raw-data-${var.environment}"
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "game-analytics-processed-data-${var.environment}"
}

# Add encryption configuration to S3 buckets
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Add versioning to S3 buckets
resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Add public access block to S3 buckets
resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Kinesis Firehose
resource "aws_kinesis_firehose_delivery_stream" "raw_data" {
  name        = "game-events-to-s3"
  destination = "s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.game_events.arn
    role_arn          = aws_iam_role.firehose_role.arn
  }

  s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.raw_data.arn
    prefix     = "raw/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"
  }
}

# Kinesis Analytics Application
resource "aws_kinesis_analytics_application" "game_analytics" {
  name = "game-analytics-processor"

  inputs {
    name_prefix = "SOURCE_SQL_STREAM"

    kinesis_stream {
      resource_arn = aws_kinesis_stream.game_events.arn
      role_arn    = aws_iam_role.kinesis_analytics_role.arn
    }

    parallelism {
      count = 1
    }

    schema_version = "1.0"

    starting_position_configuration {
      starting_position = "LATEST"
    }
  }
}

# IAM Roles and Policies
resource "aws_iam_role" "firehose_role" {
  name = "game-analytics-firehose-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "firehose.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "kinesis_analytics_role" {
  name = "game-analytics-kinesis-analytics-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "kinesisanalytics.amazonaws.com"
        }
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/game-analytics/api"
  retention_in_days = 14
}

# API Gateway
resource "aws_api_gateway_rest_api" "game_analytics" {
  name        = "game-analytics-api"
  description = "Game Analytics API"
}

resource "aws_api_gateway_resource" "events" {
  rest_api_id = aws_api_gateway_rest_api.game_analytics.id
  parent_id   = aws_api_gateway_rest_api.game_analytics.root_resource_id
  path_part   = "events"
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

# Outputs
output "api_endpoint" {
  value = aws_api_gateway_rest_api.game_analytics.execution_arn
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.game_events.name
}

output "raw_data_bucket" {
  value = aws_s3_bucket.raw_data.bucket
}

output "processed_data_bucket" {
  value = aws_s3_bucket.processed_data.bucket
}

# Add encryption to Kinesis streams
resource "aws_kinesis_stream_consumer" "game_events" {
  name       = "game-events-consumer"
  stream_arn = aws_kinesis_stream.game_events.arn

  depends_on = [aws_kinesis_stream.game_events]
}

resource "aws_kinesis_stream_consumer" "session_metrics" {
  name       = "session-metrics-consumer"
  stream_arn = aws_kinesis_stream.session_metrics.arn

  depends_on = [aws_kinesis_stream.session_metrics]
}

resource "aws_kinesis_stream_consumer" "revenue_metrics" {
  name       = "revenue-metrics-consumer"
  stream_arn = aws_kinesis_stream.revenue_metrics.arn

  depends_on = [aws_kinesis_stream.revenue_metrics]
}

# Create KMS key for Kinesis encryption
resource "aws_kms_key" "kinesis" {
  description             = "KMS key for Kinesis streams encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
}

# Get current AWS account ID
data "aws_caller_identity" "current" {} 