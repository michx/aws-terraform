# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster" {
  description = "Name of created EKS Cluster"
  type        = string
  default     = "eks-badapp"
}