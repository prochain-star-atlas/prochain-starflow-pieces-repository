from enum import Enum
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    StarAtlas Wait One Input Model
    """


class OutputModel(BaseModel):
    """
    StarAtlas Wait One Output Model
    """

    output: str = Field(
        description="Output"
    )

    
