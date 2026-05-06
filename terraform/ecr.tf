resource "aws_ecr_repository" "app_repo" {
  name                 = "devsecops-flask-app"
  force_delete = true
  image_tag_mutability = "MUTABLE"

  # Security Control: Automatically scan images on push for a second layer of defense
  image_scanning_configuration {
    scan_on_push = true
  }
}