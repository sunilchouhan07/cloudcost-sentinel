resource "random_id" "bucket_id" {
  byte_length = 4
}

resource "aws_s3_bucket" "bucket" {
  bucket = "${var.env}-logs-${random_id.bucket_id.hex}"
  force_destroy = true
  tags = {
    Name = "${var.env}-bucket"
    Project     = var.project
    Environment = var.env
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}


resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.bucket.id 
  versioning_configuration {
    status = "Enabled"
  }
}


resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  bucket = aws_s3_bucket.bucket.id 
  
  rule {
    id = "expire-old-version"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}