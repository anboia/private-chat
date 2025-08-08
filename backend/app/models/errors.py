from typing import Any, Dict, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
    
    @classmethod
    def create(
        cls,
        message: str,
        error_type: str = "invalid_request_error",
        param: Optional[str] = None,
        code: Optional[str] = None
    ) -> "ErrorResponse":
        return cls(
            error=ErrorDetail(
                message=message,
                type=error_type,
                param=param,
                code=code
            )
        )