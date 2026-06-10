variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
  default     = "clean-abacus-497115-g2"
}


variable "region" {
  description = "Google Cloud region for all resources"
  type        = string
  default     = "us-central1"
}


variable "gitlab_token" {
  description = "GitLab Personal Access Token with api scope"
  type        = string
  sensitive   = true
}


variable "webhook_signing_token" {
  description = "GitLab webhook signing token starting with whsec_"
  type        = string
  sensitive   = true
}


variable "vertex_agent_id" {
  description = "Vertex AI Reasoning Engine resource name"
  type        = string
  default     = ""
}

