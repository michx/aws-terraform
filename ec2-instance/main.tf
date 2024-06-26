terraform {
  required_version = ">= 0.12"
}



variable "vpc_id" {}
variable "cidr_block" {}
variable "av_zone" {}

resource "aws_vpc" "main" {
   cidr_block = "10.0.0.0/16"
   tags = {
    terraform = "true"
    Name = "${var.vpc_id}"
  }
}


resource "aws_subnet" "example" {
    vpc_id            = aws_vpc.main.id
    availability_zone = "${var.av_zone}"
    cidr_block        = "${cidrsubnet(var.cidr_block, 4, 1)}"
}

resource "aws_network_interface" "MyAWSResource" {
   subnet_id = aws_subnet.example.id
   }


resource "aws_instance" "test1" {
   ami             = "ami-01b799c439fd5516a"
   instance_type   = "t2.micro"
   network_interface {
    network_interface_id = aws_network_interface.MyAWSResource.id
    device_index = 0
   }
}

