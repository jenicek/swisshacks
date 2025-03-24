resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project}-${var.environment}-frontend"
  force_destroy = true

  tags = {
    Name        = "${var.project}-${var.environment}-frontend"
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

resource "aws_s3_bucket_cors_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_ownership_controls" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  depends_on = [aws_s3_bucket_public_access_block.frontend]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# CloudFront Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "frontend" {
  comment = "OAI for ${var.project}-${var.environment} frontend"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  wait_for_deployment = false

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend.cloudfront_access_identity_path
    }
  }

  # Backend API origin - using HTTP for initial connection
  origin {
    domain_name = var.backend_alb_dns_name
    origin_id   = "ALB-Backend"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"  # Use HTTP for CloudFront to ALB communication initially
      origin_ssl_protocols   = ["TLSv1.2"]
      origin_keepalive_timeout = 60
      origin_read_timeout      = 60
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # API path pattern behavior - proxying all API requests to ALB
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-Backend"

    forwarded_values {
      query_string = true
      # Forward all headers to preserve API request integrity
      headers      = ["*"]  # Forward all headers to ensure request integrity

      cookies {
        forward = "all"
      }
    }

    # Don't cache API responses by default
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0

    # Increase connection timeout for API requests
    # Note: This is handled through the origin configuration instead
  }

  # Custom error response for API timeouts
  custom_error_response {
    error_code            = 504
    response_code         = 504
    response_page_path    = "/index.html"  # Must specify a response page path if response_code is provided
    error_caching_min_ttl = 0              # Don't cache errors
  }

  # Custom error response for SPA routing
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "${var.project}-${var.environment}-cloudfront"
    Environment = var.environment
    Project     = var.project
  }
}