resource "aws_ecr_repository" "app_repo" {
  name                 = "${var.project_name}-app"
  force_delete         = true
  image_tag_mutability = "IMMUTABLE"

  encryption_configuration {
    encryption_type = "AES256"
  }

  # Security Control: Automatically scan images on push for a second layer of defense
  image_scanning_configuration {
    scan_on_push = true
  }
}
