##################################################################################
# RESOURCES
##################################################################################

# Nerworking
resource "aws_eip" "eip" {
    vpc = true
}

resource "aws_nat_gateway" "ngw" {
    allocation_id = aws_eip.eip.id
    subnet_id = aws_subnet.subnet1.id
}

resource "aws_subnet" "subnet-p" {
    cidr_block              = var.subnet_private_address_space
    vpc_id                  = aws_vpc.vpc.id
    availability_zone       = data.aws_availability_zones.available.names[0]
}

# Routing
resource "aws_route_table" "rtb-p" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id  = aws_nat_gateway.ngw.id
    }
}

resource "aws_route_table_association" "rtb-subnet-p" {
    subnet_id      = aws_subnet.subnet-p.id
    route_table_id = aws_route_table.rtb-p.id
}

# Lambda
resource "aws_lambda_function" "comic_crawler" {
    function_name = "ComicCrawler"

    role = aws_iam_role.lambda_exec.arn
    
    timeout = 900
    memory_size = 1024

    image_uri = "${aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
    package_type = "Image"

    vpc_config {
        security_group_ids = [aws_security_group.db-sg.id]
        subnet_ids = [aws_subnet.subnet-p.id]
    }

    environment {
        variables = {
            req_file    = "/var/task/${basename(var.req_file)}"
            db_host     = element(split(":", aws_db_instance.comic-db.endpoint), 0)
            db_port     = element(split(":", aws_db_instance.comic-db.endpoint), 1)
            db_name     = "comicdb"
            db_user     = var.db_username
            db_pass     = var.db_password
        }
    }
}

# IAM role which dictates what other AWS services the Lambda function
# may access.
resource "aws_iam_role" "lambda_exec" {
    name = "comic_reader_lambda"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
    role       = aws_iam_role.lambda_exec.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

