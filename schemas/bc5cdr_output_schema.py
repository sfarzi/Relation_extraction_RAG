from pydantic import BaseModel


class OneRecord(BaseModel):
    id: int
    title: str
    abstract: str
    gold_relations_mesh: list[list]
    pred_relations_mesh: list[list]
    gold_relations_term: list[list[list]]
    pred_relations_term: list[list]

class Bc5cdrOutputSchema(BaseModel):
    phase: int
    dataset: str
    LLM: str
    method: str
    split: str
    temperature: float | int
    system_prompt: str
    time: str
    results: list[OneRecord]