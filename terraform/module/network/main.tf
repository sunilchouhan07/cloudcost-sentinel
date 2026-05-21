
# VPC with Components public submet, Internet gateway, Route table & Association

resource "aws_vpc" "vpc" {
  cidr_block = "10.20.0.0/16"
  tags = {
    Name        = "${var.env}-vpc"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.vpc.id
  for_each          = var.public_subnets
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.az

  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.env}-${each.key}"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name        = "${var.env}-igw"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name        = "${var.env}-public-rt"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}


resource "aws_route_table_association" "rt_association" {
  for_each       = aws_subnet.public_subnet
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public_rt.id
}




# Security Group with inbound opned 80,443 and 22

resource "aws_security_group" "sg" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name        = "${var.env}-sg"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
    description = "SSH"
  }
}

