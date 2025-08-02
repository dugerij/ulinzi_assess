from typing import Optional
from pydantic import BaseModel, Field

class Headline(BaseModel):
    """ Model representing a news headline to be classified."""
    text: str = Field(description = "The headline to be classified")

class ClassificationResponse(BaseModel):
    """ Model representing the classification result of a news headline."""
    classification: str = Field(description="Assigned class")
    confidence: float = Field(description="Consider score of the classification")

class  RequestLogResponse(BaseModel):
    """ Model representing the response for a request log."""
    request_id: str = Field(description="Unique identifier for the request")
    submitted_headline: str = Field(description="The headline submitted for classification")
    senitment: str = Field(description="Sentiment classification result")
    status: str = Field(description="Status of the request")
    requested_at: Optional[str] = Field(description="Timestamp when the request was made")