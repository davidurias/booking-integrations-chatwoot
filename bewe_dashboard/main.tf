terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}

module "lambda" {
  source  = "app.terraform.io/nx/lambda/aws"
  version = ">=1.0.0"

  ## Lambda General
  mode = "apigw-lambda"
  name = "chatwoot-dashboard-api"

  handler     = "index.handler"
  runtime     = "python3.13"
  memory_size = 256
  timeout     = 15

  layers = [
    local.integrations_layer,
  ]

  xray_enabled     = true
  bucket_artifacts = local.bucket_artifacts_id

  env_vars = {
    "DB_NAME" = "integrations"
  }
 
  ##DB Settings
  db_id    = local.db_id
  db_host  = local.db_host
  db_port  = local.db_port
  db_sg_id = local.db_sg_id
  db_user  = local.db_user

  #Cache Settings
  cache_host  = local.cache_host
  cache_port  = local.cache_port
  cache_sg_id = local.cache_sg_id
  cache_db    = 0

  #Lambda Networking
  vpc_id     = local.vpc_id
  subnets_id = local.subnets_private

  ##LAMBDA LOGGING
  cwlog_retention = 30

  #API GW SETTINGS
  apigw_id            = local.apigw_api_id
  apigw_route         = "GET /integrations/chatwoot/bewe/dashboard"
  apigw_role_arn      = local.apigw_api_iam_role_arn

  alarm_topic = local.topic_owner_arn
} 