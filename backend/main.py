from uuid import UUID
from fastapi import FastAPI, APIRouter
from backend.utils import verify_env_vars
from backend.config import ENV, API_VERSION
from backend.service_dependency import init_db, initialize_services
from backend.models import ClassificationResponse, Headline, RequestLogResponse
from backend.service_dependency import PredictionServiceDependency

app = FastAPI(
    title="Engineer_test",
    description="A test API to serve a HuggingFace fine-tuned model",
    docs_url="/docs",
)

ver_router = APIRouter(prefix=API_VERSION)

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "API running"}

@ver_router.get("/health", summary="App Health check", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.post(
    "/predict",
    summary="Make a prediction on NEWS heaaline",
    response_model=ClassificationResponse
)
async def make_prediction(
        headline: Headline,
        prediction_service: PredictionServiceDependency
):
    """
    Endpoint to classify the sentiment of a submitted headline.

    Args:
        headline (Headline): The headline to be classified.
        prediction_service (PredictionServiceDependency): Dependency for accessing prediction service.

    Returns:
        ClassificationResponse: The classification result with label and confidence score.
    """
    return await prediction_service.submit_request(headline)

@app.get(
    "/request_log/{request_id}",
    summary="Get a request log from the table in the database using its ID",
    response_model=RequestLogResponse
)
async def get_request_log(
        request_id: UUID,
        prediction_service: PredictionServiceDependency
):
    """
    Endpoint to retrieve a request log by its ID.

    Args:
        request_id (UUID): The unique identifier for the request log.
        prediction_service (PredictionServiceDependency): Dependency for accessing prediction service.

    Returns:
        RequestLogResponse: The request log details including headline, sentiment, status, and timestamp.
    """
    return await prediction_service.get_request_log(request_id)

@app.get("/request_logs", summary="Get all request logs")
async def get_all_request_logs(
        prediction_service: PredictionServiceDependency
):
    """
    Endpoint to retrieve all request logs.

    Args:
        prediction_service (PredictionServiceDependency): Dependency for accessing prediction service.

    Returns:
        List[RequestLogResponse]: A list of all request logs.
    """
    return await prediction_service.get_all_request_logs()

@app.on_event("startup")
async def startup_event():
    """
    Initialize the FastAPI application and set up the database and services.
    """
    verify_env_vars()
    await init_db()
    await initialize_services()

app.include_router(ver_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
