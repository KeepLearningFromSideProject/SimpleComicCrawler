
##################################################################################
# PROVIDERS
##################################################################################

provider "aws" {
    access_key = var.aws_access_key
    secret_key = var.aws_secret_key
    region     = var.region 
}

locals {
    crawl_cmd = "`pwd`/src/mysql_main.py ~/req_file.json `pwd`/scripts comicdb '${element(split(":", aws_db_instance.comic-db.endpoint), 0)}' 3306 '${var.db_username}' '${var.db_password}'"
}

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

resource "aws_subnet" "subnet1" {
    cidr_block              = var.subnet1_address_space
    vpc_id                  = aws_vpc.vpc.id
    map_public_ip_on_launch = "true"
    availability_zone       = data.aws_availability_zones.available.names[0]
}

resource "aws_subnet" "subnet2" {
    cidr_block              = var.subnet2_address_space
    vpc_id                  = aws_vpc.vpc.id
    map_public_ip_on_launch = "true"
    availability_zone       = data.aws_availability_zones.available.names[1]
}

resource "aws_db_subnet_group" "comic-db-sng" {
    name = "db-sng"
    subnet_ids = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
}

# Routing
resource "aws_route_table" "rtb" {
    vpc_id = aws_vpc.vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id  = aws_internet_gateway.igw.id
    }
}

resource "aws_route_table_association" "rtb-subnet1" {
    subnet_id      = aws_subnet.subnet1.id
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

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "db-sg" {
    name   = "db-sg"
    vpc_id = aws_vpc.vpc.id

    ingress {
        from_port   = 3306
        to_port     = 3306
        protocol    = "tcp"
        cidr_blocks = [var.network_address_space]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "lambda-sg" {
  name        = "lambda-security-group"
  description = "lambda security group"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port = 0
    to_port = 0
    protocol    = "-1"
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
resource "aws_instance" "crawler-ec2" {
    ami                    = data.aws_ami.ubuntu.id
    instance_type          = "t2.micro"
    subnet_id              = aws_subnet.subnet1.id
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
        source = var.comic_req_file
        destination = "/home/ubuntu/req_file.json"
    }

    provisioner "file" {
        source = var.proxy_pem_path
        destination = "/home/ubuntu/proxy.pem"
    }

    provisioner "remote-exec" {
        inline = [
            # Install crawler dep and build env
            "chmod 600 ~/proxy.pem",
            "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -Nf -D8080 -p ${var.proxy_port} ${var.proxy_user}@${var.proxy_host} -i ~/proxy.pem",
			"while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
            "sudo apt-get update -y && sudo apt-get install -y git unzip chromium-browser libnss3 python3-pip mysql-client-5.7",
            "wget 'https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_linux64.zip' -O temp.zip && unzip temp.zip && sudo mv chromedriver /usr/bin",

            # Init comic crawler
            "git clone https://github.com/KeepLearningFromSideProject/SimpleComicCrawler.git",
            "cd SimpleComicCrawler",
            "sudo -H pip3 install -r requirements.txt",
            "echo \"{}\" > db.json",
            
            # Init DB
            "echo '[client]' > ~/account.info",
            "echo 'user=${var.db_username}' >> ~/account.info",
            "echo 'password=${var.db_password}\n' >> ~/account.info",
			"cat ~/account.info",
            "cat ~/db_build.sql | mysql --defaults-extra-file=~/account.info -h ${element(split(":", aws_db_instance.comic-db.endpoint), 0)};",

            # Init crontab
            "(crontab -l 2>/dev/null; echo \"*/5 * * * * ${local.crawl_cmd} && killall -9 chromium-browser chromedriver\") | crontab -",

        ]
    }
}

resource "aws_db_instance" "comic-db" {
    allocated_storage      = 10
    engine                 = "mysql"
    engine_version         = "8.0.20"
    instance_class         = "db.t2.micro"
    name                   = "comicdb"
    username               = var.db_username
    password               = var.db_password
    db_subnet_group_name   = aws_db_subnet_group.comic-db-sng.id
    vpc_security_group_ids = [aws_security_group.db-sg.id]
    parameter_group_name   = "default.mysql8.0"
    skip_final_snapshot    = true
    publicly_accessible    = true
}

