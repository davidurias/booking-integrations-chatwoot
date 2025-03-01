terraform {
  cloud {
    organization = "nx"
    workspaces {
      name = "booking-integrations-bewe-work"
    }
  }
}
