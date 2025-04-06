terraform {
  cloud {
    organization = "nx"
    workspaces {
      name = "booking-integrations-chatwoot-bewe-dashboard"
    }
  }
} 