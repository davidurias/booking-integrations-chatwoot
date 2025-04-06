locals {
  frontend_files = {
    "index.html" = {
      source       = "${path.module}/frontend/public/index.html"
      content_type = "text/html"
    }
    "styles.css" = {
      source       = "${path.module}/frontend/public/styles.css"
      content_type = "text/css"
    }
    "app.js" = {
      source       = "${path.module}/frontend/public/app.js"
      content_type = "application/javascript"
    }
  }
}

resource "aws_s3_bucket" "bewe_dashboard" {
  bucket = "${data.aws_caller_identity.current.account_id}-chatwoot-bewe-dashboard"
}

# Remove website configuration
# resource "aws_s3_bucket_website_configuration" "bewe_dashboard" {
#   bucket = aws_s3_bucket.bewe_dashboard.id
# 
#   index_document {
#     suffix = "index.html"
#   }
# }

# Block all public access
resource "aws_s3_bucket_public_access_block" "bewe_dashboard" {
  bucket = aws_s3_bucket.bewe_dashboard.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bucket policy allowing CloudFront OAC to GetObject
data "aws_iam_policy_document" "bewe_dashboard_s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.bewe_dashboard.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.bewe_dashboard_distribution.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "bewe_dashboard" {
  bucket = aws_s3_bucket.bewe_dashboard.id
  policy = data.aws_iam_policy_document.bewe_dashboard_s3_policy.json
}

resource "aws_s3_object" "frontend_files" {
  for_each = local.frontend_files

  bucket       = aws_s3_bucket.bewe_dashboard.id
  key          = each.key
  source       = each.value.source
  content_type = each.value.content_type
  etag         = filemd5(each.value.source)
} 