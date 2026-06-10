terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}


provider "google" {
  project = var.project_id
  region  = var.region
}


resource "google_artifact_registry_repository" "nightshift" {
  location      = var.region
  repository_id = "nightshift"
  format        = "DOCKER"
}


resource "google_secret_manager_secret" "gitlab_token" {
  secret_id = "nightshift-gitlab-token"
  replication {
    auto {}
  }
}


resource "google_secret_manager_secret_version" "gitlab_token" {
  secret      = google_secret_manager_secret.gitlab_token.id
  secret_data = var.gitlab_token
}
resource "google_secret_manager_secret" "webhook_signing_token" {
  secret_id = "nightshift-webhook-signing-token"
  replication {
    auto {}
  }
}


resource "google_secret_manager_secret_version" "webhook_signing_token" {
  secret      = google_secret_manager_secret.webhook_signing_token.id
  secret_data = var.webhook_signing_token
}


resource "google_service_account" "nightshift_sa" {
  account_id   = "nightshift-sa"
  display_name = "NightShift Service Account"
}


resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.nightshift_sa.email}"
}


resource "google_project_iam_member" "datastore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.nightshift_sa.email}"
}
resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.nightshift_sa.email}"
}


resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.nightshift_sa.email}"
}


resource "google_cloud_run_v2_service" "nightshift" {
  name     = "nightshift"
  location = var.region


  template {
    service_account = google_service_account.nightshift_sa.email


    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/nightshift/nightshift:latest"


      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "VERTEX_AGENT_ID"
        value = var.vertex_agent_id
      }


      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }


    timeout = "300s"
    max_instance_request_concurrency = 10
  }


  ingress = "INGRESS_TRAFFIC_ALL"
}


resource "google_cloud_run_v2_service_iam_member" "public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.nightshift.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}



