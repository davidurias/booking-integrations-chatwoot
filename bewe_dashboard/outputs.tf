output "dashboard_website_endpoint" {
  description = "The website endpoint for the S3 bucket hosting the dashboard"
  value       = "http://${aws_s3_bucket.bewe_dashboard.bucket}.s3-website-${data.aws_region.current.name}.amazonaws.com"
} 