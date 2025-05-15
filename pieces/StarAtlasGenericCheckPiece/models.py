from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    StarAtlas Dock Piece Input Model
    """

    value_to_test: str = Field(
        default="",
        description="Value To Test",
    )

    required_field: str = Field(
        default="",
        description="Required Field",
    )

