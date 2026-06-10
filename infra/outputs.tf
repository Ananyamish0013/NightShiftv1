output "cloud_run_url" {
  description = "Cloud Run service URL - use this as your GitLab webhook URL with /webhook appended"
  value       = google_cloud_run_v2_service.nightshift.uri
}


output "service_account_email" {
  description = "NightShift service account email"
  value       = google_service_account.nightshift_sa.email
}


output "artifact_registry_url" {
  description = "Docker image registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/nightshift/nightshift:latest"
}

