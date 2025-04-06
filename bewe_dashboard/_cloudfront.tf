resource "aws_cloudfront_origin_access_control" "bewe_dashboard_oac" {
  name                              = "${aws_s3_bucket.bewe_dashboard.id}-oac"
  description                       = "OAC for Bewe Dashboard S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "bewe_dashboard_distribution" {
  origin {
    domain_name              = aws_s3_bucket.bewe_dashboard.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.bewe_dashboard_oac.id
    origin_id                = "S3-${aws_s3_bucket.bewe_dashboard.id}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for Bewe Dashboard"
  default_root_object = "index.html"

  # logging_config {
  #   include_cookies = false
  #   bucket          = "your-logging-bucket.s3.amazonaws.com" # OPTIONAL: Specify a bucket for access logs
  #   prefix          = "cloudfront-bewe-dashboard/"
  # }

  aliases = [] # Add custom domain names here if needed later

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.bewe_dashboard.id}"

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

  # Price Class - Adjust as needed (PriceClass_100 is cheapest - US/EU only)
  price_class = "PriceClass_100"

  # Use default CloudFront certificate
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name        = "bewe-dashboard-distribution"
    Project     = "ChatwootBeweIntegration"
  }
}

output "bewe_dashboard_cloudfront_url" {
  description = "The HTTPS URL for the Bewe Dashboard served via CloudFront"
  value       = "https://${aws_cloudfront_distribution.bewe_dashboard_distribution.domain_name}"
} 