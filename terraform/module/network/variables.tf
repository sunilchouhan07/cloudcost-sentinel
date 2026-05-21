variable "vpc_cidr_block" {
  type = string
}

variable "env" {
  type = string
}

variable "ssh_cidr" {
  type = string
}

variable "public_subnets" {
  type = map(object({
    cidr_block = string
    az         = string
  }))
}

variable "project" {
  type = string
}

variable "owner" {
  type = string
}



