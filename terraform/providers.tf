terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2" # Feel free to change this to your preferred region
  
  default_tags {
    tags = {
      Environment = "dev"
      Project     = "DevSecOps-Portfolio"
      ManagedBy   = "Terraform"
    }
  }
}