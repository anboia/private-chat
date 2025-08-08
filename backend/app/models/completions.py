from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[str], List[int], List[List[int]]]
    suffix: Optional[str] = None
    max_tokens: Optional[int] = Field(default=16, ge=1)
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1, le=128)
    stream: Optional[bool] = False
    logprobs: Optional[int] = Field(default=None, ge=0, le=5)
    echo: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    best_of: Optional[int] = Field(default=1, ge=1, le=20)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LogProbs(BaseModel):
    tokens: List[str]
    token_logprobs: List[Optional[float]]
    top_logprobs: List[Optional[Dict[str, float]]]
    text_offset: List[int]


class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[LogProbs] = None
    finish_reason: Optional[str] = None


class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Optional[Usage] = None