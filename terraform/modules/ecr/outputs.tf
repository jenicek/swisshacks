output "repository_url" {
  description = "The URL of the ECR repositories"
  value = {
    backend  = aws_ecr_repository.backend.repository_url
    frontend = aws_ecr_repository.frontend.repository_url
  }
}