resource "aws_iam_user" "deploy_user" {
  name = "${var.project}-${var.environment}-deploy-user"
  path = "/"

  tags = {
    Name        = "${var.project}-${var.environment}-deploy-user"
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_iam_access_key" "deploy_user_key" {
  user = aws_iam_user.deploy_user.name
}

resource "aws_iam_policy" "deploy_policy" {
  name        = "${var.project}-${var.environment}-deploy-policy"
  description = "Policy for deployment to ${var.project}-${var.environment}"
  policy      = file("${path.module}/../../aws_deploy_policy.json")

  tags = {
    Name        = "${var.project}-${var.environment}-deploy-policy"
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_iam_user_policy_attachment" "deploy_user_policy_attachment" {
  user       = aws_iam_user.deploy_user.name
  policy_arn = aws_iam_policy.deploy_policy.arn
}

# Optional: Create OpenID Connect Provider for GitHub Actions
resource "aws_iam_openid_connect_provider" "github_actions" {
  count = var.create_oidc_provider ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["a031c46782e6e6c662c2c87c76da9aa62ccabd8e"]
}

# Optional: IAM Role for GitHub Actions to assume via OIDC
resource "aws_iam_role" "github_actions_role" {
  count = var.create_oidc_provider ? 1 : 0

  name = "${var.project}-${var.environment}-github-actions-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRoleWithWebIdentity"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions[0].arn
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project}-${var.environment}-github-actions-role"
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_iam_role_policy_attachment" "github_actions_role_policy_attachment" {
  count = var.create_oidc_provider ? 1 : 0

  role       = aws_iam_role.github_actions_role[0].name
  policy_arn = aws_iam_policy.deploy_policy.arn
}