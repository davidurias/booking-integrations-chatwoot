provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      tfc-workspace = terraform.workspace
      repo          = "https://github.com/davidurias/booking-integrations-chatwoot"
    }
  }
}
