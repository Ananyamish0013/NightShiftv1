from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import logging
from webhook_handler import router as webhook_router
from job_manager import get_recent_jobs
from google.cloud import firestore
from config import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title='NightShift', version='1.0.0')
app.include_router(webhook_router)




@app.get('/health')
async def health() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={'status': 'healthy', 'service': 'nightshift', 'version': '1.0.0'}
    )

@app.get('/jobs')
async def list_jobs() -> JSONResponse:
    jobs = get_recent_jobs(limit=20)
    return JSONResponse(
        status_code=200,
        content={'jobs': jobs, 'count': len(jobs)}
    )

@app.get('/executions')
async def list_executions(job_id: str) -> JSONResponse:
    db = firestore.Client(project=config.project_id)
    docs = (
        db.collection(config.firestore_collection_executions)
        .where('job_id', '==', job_id)
        .order_by('step_number')
        .stream()
    )
    steps = []
    for doc in docs:
        data = doc.to_dict()
        data['id']= doc.id
        if data.get('timestamp'):
            data['timestamp'] = data['timestamp'].isoformat()
        steps.append(data)
    return JSONResponse(
        status_code=200,
        content = {'job_id': job_id, 'steps':steps}
    )
if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8080,
        reload = False
    )