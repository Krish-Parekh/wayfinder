locals {
  namespace  = "wayfinder"
  memory_arn = "arn:aws:bedrock-agentcore:${var.region}:${data.aws_caller_identity.current.account_id}:memory/${var.memory_id}"
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "pod_identity_trust" {
  statement {
    actions = ["sts:AssumeRole", "sts:TagSession"]
    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "bedrock_invoke" {
  statement {
    sid       = "InvokeModels"
    actions   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "memory" {
  statement {
    sid = "TravellerMemory"
    actions = [
      "bedrock-agentcore:CreateEvent",
      "bedrock-agentcore:RetrieveMemoryRecords",
      "bedrock-agentcore:ListMemoryRecords",
      "bedrock-agentcore:GetMemory",
    ]
    resources = [local.memory_arn]
  }
}

resource "aws_iam_role" "specialist" {
  name               = "${var.cluster_name}-specialist"
  assume_role_policy = data.aws_iam_policy_document.pod_identity_trust.json
}

resource "aws_iam_role_policy" "specialist_bedrock" {
  role   = aws_iam_role.specialist.id
  policy = data.aws_iam_policy_document.bedrock_invoke.json
}

resource "aws_eks_pod_identity_association" "specialist" {
  cluster_name    = module.eks.cluster_name
  namespace       = local.namespace
  service_account = "specialist"
  role_arn        = aws_iam_role.specialist.arn
}

resource "aws_iam_role" "orchestrator" {
  name               = "${var.cluster_name}-orchestrator"
  assume_role_policy = data.aws_iam_policy_document.pod_identity_trust.json
}

resource "aws_iam_role_policy" "orchestrator_bedrock" {
  role   = aws_iam_role.orchestrator.id
  policy = data.aws_iam_policy_document.bedrock_invoke.json
}

resource "aws_iam_role_policy" "orchestrator_memory" {
  role   = aws_iam_role.orchestrator.id
  policy = data.aws_iam_policy_document.memory.json
}

resource "aws_eks_pod_identity_association" "orchestrator" {
  cluster_name    = module.eks.cluster_name
  namespace       = local.namespace
  service_account = "orchestrator"
  role_arn        = aws_iam_role.orchestrator.arn
}
