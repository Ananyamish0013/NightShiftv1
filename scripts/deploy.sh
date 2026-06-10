#!/bin/bash
set -e


PROJECT_ID=clean-abacus-497115-g2
REGION=us-central1
GITLAB_USERNAME=${GITLAB_USERNAME:-''}
IMAGE_URL=${REGION}-docker.pkg.dev/${PROJECT_ID}/nightshift/nightshift:latest


if [ -z "$GITLAB_USERNAME" ]; then
  echo 'Error: GITLAB_USERNAME environment variable is not set'
  echo 'Run: export GITLAB_USERNAME=your-gitlab-username'
  exit 1
fi


echo 'Configuring Docker authentication...'
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet


echo 'Building Docker image...'
cd backend
docker build -t ${IMAGE_URL} .
cd ..


echo 'Pushing image to Artifact Registry...'
docker push ${IMAGE_URL}


echo 'Deploying to Cloud Run...'
gcloud run deploy nightshift \
  --image ${IMAGE_URL} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --platform managed \
  --allow-unauthenticated \
  --service-account nightshift-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --memory 2Gi \
  --cpu 2 \
  --timeout 540 \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION},GITLAB_USERNAME=${GITLAB_USERNAME},GITLAB_MCP_URL=https://gitlab.com/-/cloud/duo_workflow/mcp


echo 'Getting service URL...'
SERVICE_URL=$(gcloud run services describe nightshift \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --format 'value(status.url)')


echo ''
echo 'Deployment complete!'
echo 'Service URL:' ${SERVICE_URL}
echo 'Webhook URL:' ${SERVICE_URL}/webhook
echo ''
echo 'Update your GitLab webhook URL to:' ${SERVICE_URL}/webhook


