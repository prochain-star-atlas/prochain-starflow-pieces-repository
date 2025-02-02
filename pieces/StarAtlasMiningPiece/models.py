from pydantic import BaseModel, Field


class InputModel(BaseModel):
    """
    StarAtlas Mining Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint: str = Field(
        default="",
        description="Resource to mine",
    )

    planet_pk: str = Field(
        default=0,
        description="Planet Public Key to Mine",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Mining Piece Output Model
    """
    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    resource_mint_mined: str = Field(
        description="Resource Mint Mined"
    )

    resource_amount_mined: int = Field(
        description="Amount Resource Mined"
    )

    
