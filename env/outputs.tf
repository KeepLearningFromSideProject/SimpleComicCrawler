
##################################################################################
# OUTPUT
##################################################################################

output "aws_rdb_endpoint" {
    value = aws_db_instance.comic-db.endpoint
}

output "aws_ec2_dns" {
    value = aws_instance.crawler-ec2.public_dns
}
