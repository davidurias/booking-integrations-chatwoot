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

resource "aws_s3_bucket_website_configuration" "bewe_dashboard" {
  bucket = aws_s3_bucket.bewe_dashboard.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "bewe_dashboard" {
  bucket = aws_s3_bucket.bewe_dashboard.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "bewe_dashboard" {
  bucket = aws_s3_bucket.bewe_dashboard.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.bewe_dashboard.arn}/*"
      },
    ]
  })

  depends_on = [
    aws_s3_bucket_public_access_block.bewe_dashboard,
    aws_s3_bucket.bewe_dashboard
  ]
}

resource "aws_s3_object" "frontend_files" {
  for_each = local.frontend_files

  bucket       = aws_s3_bucket.bewe_dashboard.id
  key          = each.key
  source       = each.value.source
  content_type = each.value.content_type
  etag         = filemd5(each.value.source)
} 