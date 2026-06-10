FROM python:3.11-slim
WORKDIR /app
# Install Node.js + npm + npx
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    apt-get clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY .mcp-auth /root/.mcp-auth
RUN mkdir -p /app/agent && \
    mv /app/agent_instructions.txt /app/agent/agent_instructions.txt
ENV PORT=8080
ENV GCP_PROJECT_ID=clean-abacus-497115-g2
ENV GCP_REGION=us-central1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]