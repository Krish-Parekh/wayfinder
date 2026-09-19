terraform {
  required_version = ">= 1.15"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.65"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project = "wayfinder"
      Stage   = "6"
    }
  }
}
