resource "aws_ecr_repository" "wayfinder" {
  name         = var.cluster_name
  force_delete = true

  image_scanning_configuration {
    scan_on_push = false
  }
}
