output "ecr_repository_name" {
  description = "Name of the SmokeStack API ECR repository."
  value       = aws_ecr_repository.api.name
}

output "ecr_repository_url" {
  description = "URL of the SmokeStack API ECR repository."
  value       = aws_ecr_repository.api.repository_url
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group."
  value       = aws_cloudwatch_log_group.api.name
}

output "github_actions_policy_name" {
  description = "Name of the IAM policy for CI image publishing."
  value       = aws_iam_policy.github_actions_ecr_publish.name
}