from typing import Dict, List
from aistudio_requests.schemas import PromptTemplate


class QueryTemplate(PromptTemplate):
    query_type: str
    programming_language: str
    db_params: Dict[str, str | List[str]]


class ComplexQueryTemplate(QueryTemplate):
    db_mapping: Dict[str, str]


class TableToNaturalTemplate(PromptTemplate):
    data: str
    original_prompt: str
