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

    resource_mint_to_craft: str = Field(
        default="",
        description="Resource Mint To Craft",
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
    resource_mint_crafted: str = Field(
        description="Resource Mint Crafted",
    )

    resource_amount_crafted: int = Field(
        description="Resource Amount Crafted",
    )
