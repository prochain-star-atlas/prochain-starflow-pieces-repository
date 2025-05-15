from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    Pause Workflow Piece Input Model
    """

    workflow_name: str = Field(
        default="",
        description="Workflow Name To Start",
    )

class OutputModel(BaseModel):
    """
    Pause Workflow Piece Output Model
    """
    
    message: str = Field(
        description="Sleep piece executed"
    )
