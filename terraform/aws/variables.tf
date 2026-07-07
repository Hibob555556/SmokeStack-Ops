variable "app_name" {
  description = "Application name used for AWS resource naming."
  type        = string
  default     = "smokestack"
}

variable "environment" {
  description = "Environment name used for resource naming and tagging."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for the infrastructure blueprint."
  type        = string
  default     = "us-west-2"
}