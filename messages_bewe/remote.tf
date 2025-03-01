data "terraform_remote_state" "baseline" {
  backend = "remote"

  config = {
    organization = "nx"

    workspaces = {
      name = "booking-aws-baseline"
    }
  }
}
