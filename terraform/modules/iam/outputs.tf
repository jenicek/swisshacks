output "deploy_user_name" {
  description = "Name of the deployment IAM user"
  value       = aws_iam_user.deploy_user.name
}

output "deploy_user_arn" {
  description = "ARN of the deployment IAM user"
  value       = aws_iam_user.deploy_user.arn
}

output "deploy_access_key_id" {
  description = "Access key ID for the deployment user"
  value       = aws_iam_access_key.deploy_user_key.id
}

output "deploy_secret_access_key" {
  description = "Secret access key for the deployment user"
  value       = aws_iam_access_key.deploy_user_key.secret
  sensitive   = true
}

output "deploy_policy_arn" {
  description = "ARN of the deployment policy"
  value       = "arn:aws:iam::aws:policy/AdministratorAccess"
}

output "github_actions_role_arn" {
  description = "ARN of the GitHub Actions role"
  value       = var.create_oidc_provider ? aws_iam_role.github_actions_role[0].arn : null
}