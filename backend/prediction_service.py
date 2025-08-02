from uuid import UUID

from sqlalchemy import select

import torch
from transformers import pipeline

from backend.service_dependency import AsyncSession
from backend.models import ClassificationResponse, Headline, RequestLogResponse
from backend.schemas import RequestLog

sentiment_pipeline = pipeline(
    "text-classification", 
    model="Dugerij/news_sentiment_classifier",
    device=0 if torch.cuda.is_available() else -1
)

reverse_label_map = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

class PredictionService:
    """
    A service class to handle prediction-related operations,
    including saving request logs and retrieving them.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initilize the PredictionService with a database session.
        """
        self.db_session = db_session

    async def submit_request(self, headline: Headline) -> ClassificationResponse:
        """
        Classify the sentiment of a submitted headline.
        """
        try:
            if not headline.text:
                raise ValueError("Please provide a NEWS headline for sentiment classification")
            result = sentiment_pipeline(headline.text, truncation=True)[0]

            result["label"] = reverse_label_map.get(result["label"], "unknown")
            request_log = RequestLog.from_request(headline, result, status="success")

            self.db_session.add(request_log)
            await self.db_session.commit()
            
            return ClassificationResponse(
                classification=result["label"],
                confidence=result["score"]
            )
        except Exception as e:
            request_log = RequestLog.from_request(
                headline, 
                {"label": "error", "score": 0.0},
                status="failed"
            )
            self.db_session.add(request_log)
            await self.db_session.commit()

            raise Exception(f"Error processing request: {str(e)}")
        
    async def get_request_log(
            self,
            request_id: UUID
    ) -> RequestLogResponse:
        """
        Retrieve a request log by its ID.
        Parameters:
            request_id (UUID): The Unique ID linked to a request log.
        """
        try:
            query = select(RequestLog).where(RequestLog.request_id == request_id)
            result = await self.db_session.execute(query)
            log = result.scalar_one_or_none()

            if not log:
                raise Exception(f"Request log with ID {request_id} not found")

            return RequestLogResponse(
                request_id=str(log.request_id),
                submitted_headline=log.submitted_headline,
                senitment=log.senitment,
                status=log.status,
                requested_at=log.requested_at.isoformat() if log.requested_at else None
            )
        except Exception as e:
            raise Exception(f"Error retrieving request log: {str(e)}")

    async def get_all_request_logs(
        self,
        ) -> list[RequestLogResponse]:
        """
        Retrieve all request logs.
        """
        try:
            query = select(RequestLog)
            result = await self.db_session.execute(query)
            rlogs = result.scalars().all()

            return [
                RequestLogResponse(
                    request_id=str(rlog.request_id),
                    submitted_headline=rlog.submitted_headline,
                    senitment=rlog.senitment,
                    status=rlog.status,
                    requested_at=rlog.requested_at.isoformat() if rlog.requested_at else None
                ) for rlog in rlogs
            ]
        except Exception as e:
            raise Exception(f"Error retrieving all request logs: {str(e)}")