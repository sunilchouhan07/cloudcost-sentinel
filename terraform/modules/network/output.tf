output "vpc_id" {
  value = aws_vpc.vpc.id
}

output "subnet_ids" {
  value = [for subnet in aws_subnet.public_subnet : subnet.id]
}

output "security_group_id" {
  value = aws_security_group.sg.id
}

