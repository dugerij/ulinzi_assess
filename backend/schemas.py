from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UUID, Column, String, TIMESTAMP
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()

class RequestLog(BaseModel):
    """
    Represents a log entry for a request in the system.
    """
    __tablename__ = "request_log"
    request_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    submitted_headline = Column(String, nullable=False)
    senitment= Column(String, nullable=True)
    status = Column(String, nullable=False)
    requested_at = Column(type_=TIMESTAMP(timezone=True), default=datetime.utcnow)
    @classmethod
    def from_request(cls, headline: str, result: dict, status: str):
        """
        Create a RequestLog instance from a headline and result.
        """
        return cls(
            request_id=uuid4(),
            submitted_headline=headline.text,
            senitment=result["label"],
            status=status
        )

metadata = RequestLog.metadata
