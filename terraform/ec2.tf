resource "aws_instance" "web_tier" {
  count                  = var.instance_count
  ami                    = var.ami_id
  vpc_security_group_ids = [module.network.security_group_id]
  subnet_id              = module.network.subnet_ids[count.index]
  instance_type          = var.instance_type

  tags = {
    Name        = "${var.env}-web-${count.index + 1}"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}