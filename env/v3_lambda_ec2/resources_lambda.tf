##################################################################################
# RESOURCES
##################################################################################

# Lambda
resource "aws_lambda_function" "comic_crawler" {
    function_name = "comic_crawler"

    role = aws_iam_role.lambda_exec.arn
    
    timeout = 900
    memory_size = 1024

    image_uri = "${aws_ecr_repository.repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
    package_type = "Image"

    environment {
        variables = {
            req_file    = "/var/task/${basename(var.req_file)}"
            db_host     = aws_instance.crawler-ec2.public_dns
            db_port     = 3306
            db_name     = "comicdb"
            db_user     = var.db_username
            db_pass     = var.db_password
        }
    }
}

# IAM role which dictates what other AWS services the Lambda function may access.
resource "aws_iam_role" "lambda_exec" {
    name = "comic_crawler_lambda"

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

# Cloud watch
resource "aws_cloudwatch_event_rule" "every_one_hour" {
    name = "every-one-hour"
    description = "Fires one hour"
    schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "crawl_comic_every_one_hour" {
    rule = aws_cloudwatch_event_rule.every_one_hour.name
    target_id = "comic_crawler"
    arn = aws_lambda_function.comic_crawler.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_comic_crawler" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.comic_crawler.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.every_one_hour.arn
}

