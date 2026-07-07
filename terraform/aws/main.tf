locals {
  name_prefix = "${var.app_name}-${var.environment}"

  common_tags = {
    Application = "SmokeStack Ops"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "DevOps portfolio validate-only blueprint"
  }
}

# ECR repository for storing SmokeStack API container images.
# This is not applied in this portfolio project to avoid cloud costs.
resource "aws_ecr_repository" "api" {
  name                 = "${local.name_prefix}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = local.common_tags
}

# CloudWatch log group blueprint for future container/application logs.
# Retention is intentionally short for cost awareness.
resource "aws_cloudwatch_log_group" "api" {
  name              = "/${var.app_name}/${var.environment}/api"
  retention_in_days = 14

  tags = local.common_tags
}

# IAM policy document that would allow CI to publish Docker images to ECR.
# This is intentionally scoped to image publishing, not broad administrator access.
data "aws_iam_policy_document" "github_actions_ecr_publish" {
  statement {
    sid = "AllowEcrAuthToken"

    actions = [
      "ecr:GetAuthorizationToken"
    ]

    resources = ["*"]
  }

  statement {
    sid = "AllowImagePublishToSmokeStackRepository"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeRepositories",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]

    resources = [
      aws_ecr_repository.api.arn
    ]
  }
}

# Managed IAM policy blueprint for GitHub Actions ECR publishing.
resource "aws_iam_policy" "github_actions_ecr_publish" {
  name        = "${local.name_prefix}-github-actions-ecr-publish"
  description = "Allows CI to publish SmokeStack API images to the ECR repository."
  policy      = data.aws_iam_policy_document.github_actions_ecr_publish.json

  tags = local.common_tags
}