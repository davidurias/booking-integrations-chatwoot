data "aws_lambda_layer_version" "integrations_layer" {
  layer_name = "integrations-layer-python"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "terraform_remote_state" "baseline" {
  backend = "remote"
  config = {
    organization = "nx"
    workspaces = {
      name = "booking-aws-baseline"
    }
  }
} 