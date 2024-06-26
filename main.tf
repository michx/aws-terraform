terraform {
  required_version = ">= 0.12"
}


provider "aws" {
   access_key = "ASIAQVV7YLIC3VNSKNMG"
   secret_key = "sddwXg41iuvqgEtODUtasLDelK7FuhKffQ7O+PNa"
   region = "us-west-2"
}

variable "vpc_id" {}

data "aws_vpc" "selected" {
   id = "${var.vpc_id}"
}

resource "aws_subnet" "example" {
    vpc_id            = "${data.aws_vpc.selected.id}"
    availability_zone = "us-west-2a"
    cidr_block        = "${cidrsubnet(data.aws_vpc.selected.cidr_block, 4, 1)}"
}

resource "aws_network_interface" "MyAWSResource" {
   subnet_id = aws_subnet.example
   }


resource "aws_instance" "test1" {
   ami             = "ami-01b799c439fd5516a"
   instance_type   = "t2.micro"
   network_interface {
    network_interface_id = aws_network_interface.MyAWSResource
    device_index = 0
   }
}

