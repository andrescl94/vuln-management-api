terraform {
    required_version = "~> 1.2.3"

    required_providers {
      aws = {
        source = "hashicorp/aws"
        version = "~>4.15.1"
      }
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
      enabled = true
    }
    server_side_encryption {
      enabled = true
    }

    global_secondary_index {
      name = "main_index"
      hash_key = "hk"
      range_key = "rk"
      projection_type = "ALL"
    }
    global_secondary_index {
      name = "inverted_index"
      hash_key = "rk"
      range_key = "hk"
      projection_type = "ALL"
    }
}