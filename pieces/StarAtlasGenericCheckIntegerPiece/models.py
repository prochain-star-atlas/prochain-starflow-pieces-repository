from pydantic import BaseModel, Field

class InputModel(BaseModel):
    """
    StarAtlas Dock Piece Input Model
    """

    value_to_test: int = Field(
        default=0,
        description="Value To Test",
    )

    required_field: int = Field(
        default=0,
        description="Required Field",
    )

