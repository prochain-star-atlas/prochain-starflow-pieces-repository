from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    StarAtlas Craft Piece Input Model
    """

    destination_x: int = Field(
        default=0,
        description="Coordinates of X",
    )

    destination_y: int = Field(
        default=0,
        description="Coordinates of Y",
    )

    craft_public_key: str = Field(
        default="",
        description="Craft Public Key",
    )

    resource_amount_to_craft: int = Field(
        default=0,
        description="Resource Amount To Craft",
    )

    crew_allocation_to_craft: int = Field(
        default=0,
        description="Crew Amount For Crafting",
    )

    recursive_craft: bool = Field(
        default=False,
        description="Crafting recursivly missing resources",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Craft Piece Input Model
    """
    craft_public_key: str = Field(
        description="Craft Public Key",
    )

    resource_amount_crafted: int = Field(
        description="Resource Amount Crafted",
    )
