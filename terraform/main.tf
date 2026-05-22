module "network" {
  source = "./modules/network"

  vpc_cidr_block = "10.20.0.0/16"
  ssh_cidr       = "0.0.0.0/0"
  public_subnets = {
    public_subnet_1 = {
      cidr_block = "10.20.1.0/24"
      az         = "us-east-1a"
    }

    public_subnet_2 = {
      cidr_block = "10.20.2.0/24"
      az         = "us-east-1b"
    }
  }

  env     = var.env
  project = var.project
  owner   = var.owner
}