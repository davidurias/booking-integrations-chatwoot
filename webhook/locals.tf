locals {

  integrations_layer = data.aws_lambda_layer_version.integrations_layer.arn

  bucket_artifacts_id = data.terraform_remote_state.baseline.outputs.bucket_artifacts_id

  subnets_private = data.terraform_remote_state.baseline.outputs.subnets_private
  vpc_id          = data.terraform_remote_state.baseline.outputs.vpc_id

  db_id  = data.terraform_remote_state.baseline.outputs.db_id
  db_host  = data.terraform_remote_state.baseline.outputs.db_host
  db_port  = data.terraform_remote_state.baseline.outputs.db_port
  db_sg_id = data.terraform_remote_state.baseline.outputs.db_sg_id
  db_user  = "integrations"

  cache_host  = try(data.terraform_remote_state.baseline.outputs.cache_host, null)
  cache_port  = try(data.terraform_remote_state.baseline.outputs.cache_port, null)
  cache_sg_id = try(data.terraform_remote_state.baseline.outputs.cache_sg_id, null)

  apigw_api_id       = data.terraform_remote_state.baseline.outputs.apigw_api_id
  apigw_api_iam_role_arn = data.terraform_remote_state.baseline.outputs.apigw_api_iam_role_arn

  topic_owner_arn = data.terraform_remote_state.baseline.outputs.topic_owner_arn

}
