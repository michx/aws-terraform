
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

variable "cluster_name" {
  type = string
}

variable "region" {
  type = string
}
resource "aws_iam_role" "role_for_appbuild" {
  name               = "role_for_appbuild"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "policy_cb" {
 statement {
    actions = [
        "eks:AccessKubernetesApi",
        "eks:CreateAddon",
        "eks:CreateEksAnywhereSubscription",
        "eks:DeleteAddon",
        "eks:DescribeAddon",
        "eks:DescribeCluster",
        "eks:DescribeNodegroup",
        "eks:DescribePodIdentityAssociation",
        "eks:DisassociateAccessPolicy",
        "eks:DisassociateIdentityProviderConfig",
        "eks:ListAccessEntries",
        "eks:ListAccessPolicies",
        "eks:ListAddons",
        "eks:ListClusters",
        "eks:ListNodegroups",
        "eks:ListUpdates",
        "eks:RegisterCluster",
        "eks:TagResource",
        "eks:UntagResource",
        "eks:UpdateAccessEntry",
        "eks:UpdateAddon",
        "eks:UpdateClusterConfig",
        "eks:UpdateClusterVersion",
        "eks:UpdateNodegroupVersion",
        "eks:UpdatePodIdentityAssociation",
        "logs:*"
    ]
    effect = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "codebuild_role_policy" {
  role   = aws_iam_role.role_for_appbuild.name
  policy = data.aws_iam_policy_document.policy_cb.json
}

resource "aws_codebuild_project" "cb_project" {
  name          = "Ecommerce-app-manage"
  description   = "project to apply a K8s Manifest to EKS Cluster such as an app will run"
  build_timeout = 60
  service_role  = aws_iam_role.role_for_appbuild.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }


  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
  
    environment_variable {
      name  = "eksclustername"
      value = "${var.cluster_name}"
    }
    environment_variable {
      name  = "region"
      value = "${var.region}"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "log-group"
      stream_name = "log-stream"
    }
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/michx/aws-terraform"
    buildspec       = "Build/CodeBuild_for_vuln_deplyment/buildspec.yml"
    git_clone_depth = 1

    git_submodules_config {
      fetch_submodules = true
    }
  }

  source_version = "main"
}