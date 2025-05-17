from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    StarAtlas Dock Piece Input Model
    """

    value_to_test: int = Field(
        default="",
        description="Value To Test",
    )

    required_field: int = Field(
        default="",
        description="Required Field",
    )

