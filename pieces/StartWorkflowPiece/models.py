from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    Start Workflow Piece Input Model
    """

    workflow_name: str = Field(
        default="",
        description="Workflow Name To Start",
    )


class OutputModel(BaseModel):
    """
    Start Workflow Piece Output Model
    """
    message: str = Field(
        description="Worfklow piece executed"
    )
