from typing import List, Optional
from pydantic import BaseModel


class ModelPermission(BaseModel):
    id: str
    object: str = "model_permission"
    created: int
    allow_create_engine: bool
    allow_sampling: bool
    allow_logprobs: bool
    allow_search_indices: bool
    allow_view: bool
    allow_fine_tuning: bool
    organization: str
    group: Optional[str] = None
    is_blocking: bool


class Model(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: Optional[List[ModelPermission]] = None
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[Model]