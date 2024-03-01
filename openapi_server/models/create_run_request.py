# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401
from openapi_server.models.assistant_object_tools_inner import AssistantObjectToolsInner


class CreateRunRequest(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    CreateRunRequest - a model defined in OpenAPI

        assistant_id: The assistant_id of this CreateRunRequest.
        model: The model of this CreateRunRequest [Optional].
        instructions: The instructions of this CreateRunRequest [Optional].
        additional_instructions: The additional_instructions of this CreateRunRequest [Optional].
        tools: The tools of this CreateRunRequest [Optional].
        metadata: The metadata of this CreateRunRequest [Optional].
    """

    assistant_id: str = Field(alias="assistant_id")
    model: Optional[str] = Field(alias="model", default=None)
    instructions: Optional[str] = Field(alias="instructions", default=None)
    additional_instructions: Optional[str] = Field(alias="additional_instructions", default=None)
    tools: Optional[List[AssistantObjectToolsInner]] = Field(alias="tools", default=None)
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)

CreateRunRequest.update_forward_refs()