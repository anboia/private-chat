from typing import List, Optional, Union
from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    input: Union[str, List[str], List[int], List[List[int]]]
    model: str
    encoding_format: Optional[str] = Field(default="float", description="The format to return the embeddings in")
    dimensions: Optional[int] = Field(default=None, description="The number of dimensions the resulting output embeddings should have")
    user: Optional[str] = None


class Embedding(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int


class Usage(BaseModel):
    prompt_tokens: int
    total_tokens: int


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[Embedding]
    model: str
    usage: Usage