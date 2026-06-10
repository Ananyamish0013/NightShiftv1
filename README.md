NightShift 🌙
NightShift is an autonomous code maintenance agent that monitors your GitLab repositories, identifies issues, and opens fix branches with Merge Requests — automatically, with no human in the loop.
Instead of waiting for a developer to notice a bug, NightShift wakes up on every push, scans the codebase, and gets to work.

What It Does

A push to your GitLab repository triggers a webhook
NightShift receives the event and queues a maintenance job
An AI agent (powered by Google ADK + Gemini) scans the repository for issues
For each issue found, NightShift creates a fix branch, commits the changes, and opens a Merge Request — ready for human review

No manual intervention required between step 1 and step 4.

Architecture
GitLab Webhook
      │
      ▼
Cloud Run Service (FastAPI)
      │
      ├── webhook_handler.py   → validates signature, queues job
      ├── job_processor.py     → orchestrates agent execution
      └── agent_runner.py      → invokes ADK agent via MCP toolset
                │
                ▼
        Google ADK Agent (Gemini)
                │
                ▼
        GitLab MCP Server
        ├── read repository files
        ├── create fix branch
        ├── commit changes
        └── open Merge Request
                │
                ▼
        Firestore (job state tracking)

Tech Stack
LayerTechnologyAI AgentGoogle ADK, GeminiMCP IntegrationGitLab MCP Server (gitlab.com/api/v4/mcp)BackendFastAPI, async PythonDeploymentGoogle Cloud Run (containerized)State ManagementFirestoreAuthGitLab Personal Access Token (Bearer)ContainerizationDocker

Key Design Decisions
Stateless Cloud Run containers with Firestore state
Cloud Run containers are ephemeral and may spin up cold on every request. All job state (queued → running → complete/failed) is persisted in Firestore using merge-safe writes, so no state is lost between container instances.
MCP over direct API calls
Rather than calling GitLab's REST API directly, NightShift uses GitLab's MCP server. This means the agent can reason about which GitLab actions to take rather than following a hardcoded script — making it adaptable to different repository structures and issue types.
Strategy-pattern Demo Mode
A DEMO_MODE environment variable gates a self-contained demo agent that returns realistic results with proper Firestore state transitions and structured logs — useful for demos when MCP auth is unavailable.

Project Structure
nightshift/
├── agent_runner.py       # ADK agent invocation and MCP toolset setup
├── job_processor.py      # job orchestration and strategy pattern seam
├── webhook_handler.py    # FastAPI routes, signature validation, job queuing
├── signature.py          # GitLab webhook signature verification
├── job_manager.py        # Firestore read/write for job state
├── config.py             # environment variable parsing (os.environ only)
├── demo/
│   └── demo_agent.py     # self-contained demo mode agent
├── Dockerfile
└── requirements.txt

Setup & Deployment
Prerequisites

Google Cloud project with Cloud Run and Firestore enabled
GitLab account with a Personal Access Token (scopes: api, read_repository, write_repository)
Docker

Environment Variables
VariableDescriptionGITLAB_PATGitLab Personal Access TokenGITLAB_WEBHOOK_SECRETWebhook signing tokenGOOGLE_CLOUD_PROJECTGCP project IDDEMO_MODESet to true to run without live MCP connection
Deploy to Cloud Run
bash# Build and push container
docker build -t gcr.io/YOUR_PROJECT_ID/nightshift .
docker push gcr.io/YOUR_PROJECT_ID/nightshift

# Deploy
gcloud run deploy nightshift \
  --image gcr.io/YOUR_PROJECT_ID/nightshift \
  --platform managed \
  --region us-central1 \
  --set-env-vars GITLAB_PAT=your_token,GOOGLE_CLOUD_PROJECT=your_project_id
Configure GitLab Webhook
In your GitLab repository: Settings → Webhooks → Add new webhook

URL: your Cloud Run service URL
Trigger: Push events
Secret token: your GITLAB_WEBHOOK_SECRET


Status
Currently in active development. Core pipeline (webhook → agent → MR) is functional. MCP authentication in stateless Cloud Run containers is the active area of work.

Built With

Google ADK — agent orchestration framework
Gemini — underlying LLM
GitLab MCP Server — GitLab tool integration
Google Cloud Run — serverless container deployment
Firestore — job state persistence

