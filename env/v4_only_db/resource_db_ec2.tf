##################################################################################
# DATA
##################################################################################

data "aws_availability_zones" "available" {}

data "aws_ami" "aws-linux" {
    most_recent = true
    owners      = ["amazon"]

    filter {
        name   = "name"
        values = ["amzn-ami-hvm*"]
    }

    filter {
        name   = "root-device-type"
        values = ["ebs"]
    }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }
}

data "aws_ami" "ubuntu" {
    most_recent = true

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
    }

    filter {
        name = "virtualization-type"
        values = ["hvm"]
    }

	owners = ["099720109477"]
}

##################################################################################
# RESOURCES
##################################################################################

# Nerworking
resource "aws_vpc" "vpc" {
    cidr_block = var.network_address_space
    enable_dns_hostnames = "true"    
}

resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.vpc.id
}

resource "aws_subnet" "subnet" {
    cidr_block              = var.subnet_address_space
    vpc_id                  = aws_vpc.vpc.id
    map_public_ip_on_launch = "true"
    availability_zone       = data.aws_availability_zones.available.names[0]
}

# Routing
resource "aws_route_table" "rtb" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id  = aws_internet_gateway.igw.id
    }
}

resource "aws_route_table_association" "rtb-subnet" {
    subnet_id      = aws_subnet.subnet.id
    route_table_id = aws_route_table.rtb.id
}

# Security Group
resource "aws_security_group" "crawler-sg" {
    name   = "crawler-sg"
    vpc_id = aws_vpc.vpc.id

    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"] 
    }

    ingress {
        from_port   = 3306
        to_port     = 3306
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# Instances
resource "aws_instance" "db-ec2" {
    ami                    = data.aws_ami.ubuntu.id
    instance_type          = "t3.nano"
    subnet_id              = aws_subnet.subnet.id
    vpc_security_group_ids = [aws_security_group.crawler-sg.id]
    key_name               = var.key_name

    connection {
        type        = "ssh"
        host        = self.public_ip
        user        = "ubuntu"
        private_key = file(var.private_key_path)
    }

    provisioner "file" {
        source = var.db_sql_path
        destination = "/home/ubuntu/db_build.sql"
    }

    provisioner "file" {
        source ="${path.module}/keep-db-alive.sh"
        destination = "/home/ubuntu/keep-db-alive.sh"
    }

    provisioner "remote-exec" {
        inline = [
            "#!/bin/bash",
            "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
            "sudo apt-get update && sudo apt-get install mysql-server mysql-client -y",
            "sudo sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf",
            "sudo service mysql restart",
            "chmod +x /home/ubuntu/keep-db-alive.sh",
            "nohup /home/ubuntu/keep-db-alive.sh &",
            "sudo mysql -uroot <<<'CREATE DATABASE comicdb;'",
            "sudo mysql -uroot <<<$(cat /home/ubuntu/db_build.sql)",
            "sudo mysql -uroot <<<\"CREATE USER '${var.db_username}'@'%' IDENTIFIED BY '${var.db_password}';\"",
            "sudo mysql -uroot <<<\"GRANT ALL ON comicdb.* TO '${var.db_username}'@'%'\";"
        ]
    }
}

##################################################################################
# OUTPUT
##################################################################################

output "db_dns" {
    value = aws_instance.db-ec2.public_dns
}
