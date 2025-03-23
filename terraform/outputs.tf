output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = module.ecr.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_endpoint
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.ecs.alb_dns_name
}

output "deploy_user_name" {
  description = "Name of the deployment IAM user"
  value       = module.iam.deploy_user_name
}

output "deploy_access_key_id" {
  description = "Access key ID for the deployment user"
  value       = module.iam.deploy_access_key_id
}

output "deploy_secret_access_key" {
  description = "Secret access key for the deployment user"
  value       = module.iam.deploy_secret_access_key
  sensitive   = true
}

output "github_actions_role_arn" {
  description = "ARN of the GitHub Actions role"
  value       = module.iam.github_actions_role_arn
}