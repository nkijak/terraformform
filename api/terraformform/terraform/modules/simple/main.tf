
variable "short_id" {
  type        = string
  description = "project short id"
}

variable "env" {
  type        = string
  description = "env"
  default     = "dev"
}



terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.35.1"
    }
  }
}

locals {
  namespace = "${var.short_id}-${var.env}"
}

resource "kubernetes_namespace" "this" {
  metadata {
    name = local.namespace
  }
}

output "namespace" {
  value       = local.namespace
  description = "created namespace"
}

