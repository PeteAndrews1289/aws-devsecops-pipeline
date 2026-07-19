module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.21.0"

  cluster_name    = "${var.project_name}-cluster"
  cluster_version = var.kubernetes_version

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  # Security Control: Enable OIDC provider for IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  # EKS Managed Node Group
  eks_managed_node_groups = {
    general = {
      desired_size = 2
      min_size     = 1
      max_size     = 3

      instance_types = ["t3.small"]
      capacity_type  = "ON_DEMAND"

      ami_type = "AL2_x86_64"
    }
  }

  cluster_endpoint_public_access  = false
  cluster_endpoint_private_access = true

  cluster_enabled_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler",
  ]
}
