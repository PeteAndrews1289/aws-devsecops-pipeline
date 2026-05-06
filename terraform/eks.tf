module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "devsecops-cluster"
  cluster_version = "1.28"

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

      instance_types = ["t3.micro"]
      capacity_type  = "ON_DEMAND"

	ami_type = "AL2_x86_64"
    }
  }

  # Allow the deployer to access the cluster via the CLI
  cluster_endpoint_public_access = true
}