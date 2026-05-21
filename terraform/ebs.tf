resource "aws_ebs_volume" "orphan_volume" {
  availability_zone = "us-east-1a"
  size              = 10
  tags = {
    Name        = "${var.env}-ebs"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}