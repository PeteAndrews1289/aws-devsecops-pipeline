variable "aws_region" {
  description = "AWS region for the disposable lab."
  type        = string
  default     = "us-east-2"
}

variable "availability_zones" {
  description = "Two availability zones in aws_region."
  type        = list(string)
  default     = ["us-east-2a", "us-east-2b"]

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Exactly two availability zones are required."
  }
}

variable "project_name" {
  description = "Prefix used for lab resources and tags."
  type        = string
  default     = "devsecops-comparison-lab"
}

variable "environment" {
  description = "Environment tag applied to AWS resources."
  type        = string
  default     = "disposable-lab"
}

variable "kubernetes_version" {
  description = "A currently supported EKS Kubernetes version. This is intentionally required at plan time."
  type        = string

  validation {
    condition     = can(regex("^1\\.[0-9]{2}$", var.kubernetes_version))
    error_message = "Use an EKS version in 1.xx form after confirming current AWS support."
  }
}
