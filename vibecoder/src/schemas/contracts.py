from pydantic import BaseModel, Field


class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str

    request_schema: dict = Field(default_factory=dict)
    response_schema: dict = Field(default_factory=dict)


class APIContract(BaseModel):
    """Shared contract consumed by FE and BE workers."""

    endpoints: list[APIEndpoint]


class DatabaseModel(BaseModel):
    name: str
    fields: dict[str, str]
    relationships: list[str] = Field(default_factory=list)


class SchemaSpec(BaseModel):
    """Database schema specification."""

    models: list[DatabaseModel]