terraform {
  required_version = "~> 1.2.3"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~>4.15.1"
    }
  }
}

variable "environment" {
  default = ""
  type = string
}

variable "region" {
  default = "us-east-1"
  type = string
}

provider "aws" {
  region = var.region

  skip_credentials_validation = var.environment == "" ? true : false
  skip_metadata_api_check     = var.environment == "" ? true : false
  skip_requesting_account_id  = var.environment == "" ? true : false

  endpoints {
    dynamodb = var.environment == "" ? "http://localhost:8022" : "https://dynamodb.${var.region}.amazonaws.com"
  }
}

resource "aws_dynamodb_table" "vuln-management" {
  name = "vuln-management"
  hash_key = "hk"
  range_key = "rk"

  attribute {
    name = "hk"
    type = "S"
  }
  attribute {
    name ="rk"
    type = "S"
  }

  billing_mode = "PROVISIONED"
  read_capacity = 25
  write_capacity = 25

  point_in_time_recovery {
    enabled = var.environment == "" ? false : true
  }
  server_side_encryption {
    enabled = true
  }

  global_secondary_index {
    name = "main_index"
    hash_key = "hk"
    range_key = "rk"
    projection_type = "ALL"
    read_capacity = 25
    write_capacity = 25
  }
}
