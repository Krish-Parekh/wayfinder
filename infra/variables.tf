variable "region" {
  type    = string
  default = "ap-southeast-2"
}

variable "cluster_name" {
  type    = string
  default = "wayfinder"
}

variable "kubernetes_version" {
  type    = string
  default = "1.36"
}

variable "memory_id" {
  type        = string
  description = "AgentCore Memory id the orchestrator reads and writes. Created once by scripts/create_memory.py, not by Terraform."
  default     = "wayfinder-KkA9NN31Vi"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "az_count" {
  type    = number
  default = 2
}
