terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# This provider block is included so the infrastructure blueprint is realistic.
# The GitHub Actions workflow validates this configuration only; it does not run
# terraform plan or terraform apply.
provider "aws" {
  region = var.aws_region
}