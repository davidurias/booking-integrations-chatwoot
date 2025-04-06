resource "aws_cloudfront_origin_access_control" "bewe_dashboard_oac" {
  name                              = "${aws_s3_bucket.bewe_dashboard.id}-oac"
  description                       = "OAC for Bewe Dashboard S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_response_headers_policy" "bewe_dashboard_cors" {
  name = "bewe-dashboard-cors-policy"
  comment = "CORS policy for Bewe Dashboard allowing Chatwoot origin"
  cors_config {
    access_control_allow_credentials = false
    access_control_allow_headers {
      items = ["*"] # Allow all standard headers
    }
    access_control_allow_methods {
      items = ["GET", "HEAD", "OPTIONS"] # Methods used by the dashboard
    }
    access_control_allow_origins {
      items = ["chatwoot.novaxtreme.com"]
    }
    access_control_max_age_sec = 3600 # Cache preflight response for 1 hour
    origin_override = true
  }
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
    response_headers_policy_id = aws_cloudfront_response_headers_policy.bewe_dashboard_cors.id

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