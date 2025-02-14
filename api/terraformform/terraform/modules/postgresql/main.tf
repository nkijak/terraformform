
variable "project_id" {
  type = string
}

variable "env" {
  type = string
}


output "connection_string" {
  value = "postgres://postgres-${env}.someserver.cloud.us/${project_id}"
}
