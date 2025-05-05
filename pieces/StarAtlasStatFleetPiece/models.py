from enum import Enum
from pydantic import BaseModel, Field
from decimal import *

class InputModel(BaseModel):
    """
    StarAtlas Mining Piece Input Model
    """

    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )


class OutputModel(BaseModel):
    """
    StarAtlas Mining Piece Output Model
    """
    fleet_name: str = Field(
        default="",
        description="Fleet Name",
    )

    public_key: str = Field(
        default="",
        description="Public Key",
    )

    state: str = Field(
        default="",
        description="State",
    )

    faction: str = Field(
        default="",
        description="Faction",
    )

    warp_fuel_consumption_rate: int = Field(
        description="Warp Fuel Consumption Rate"
    )

    warp_speed: int = Field(
        description="Warp Speed"
    )

    max_warp_distance: int = Field(
        description="Max Warp Distance"
    )

    subwarp_fuel_consumption_rate: int = Field(
        description="Subwarp Fuel Consumption Rate"
    )

    subwarp_speed: int = Field(
        description="Subwarp Speed"
    )

    cargo_capacity: int = Field(
        description="Cargo Capacity"
    )

    fuel_capacity: int = Field(
        description="Fuel Capacity"
    )

    ammo_capacity: int = Field(
        description="Ammo Capacity"
    )

    scan_cost: int = Field(
        description="Scan Cost"
    )

    require_crew: int = Field(
        description="Require Crew"
    )

    passenger_capacity: int = Field(
        description="Passenger Capacity"
    )

    crew_count: int = Field(
        description="Crew Count"
    )

    rented_crew: int = Field(
        description="Rented Crew"
    )

    respawn_time: int = Field(
        description="Respawn Time"
    )

    sdu_per_scan: int = Field(
        description="Sdu Per Scan"
    )

    scan_cooldown: int = Field(
        description="Scan Cooldown"
    )

    warp_cooldown: int = Field(
        description="Warp Cooldown"
    )

    mining_rate: int = Field(
        description="Mining Rate"
    )

    food_consumption_rate: int = Field(
        description="Food Consumption Rate"
    )

    ammo_consumption_rate: int = Field(
        description="Ammo Consuption Rate"
    )

    planet_exit_fuel_amount: int = Field(
        description="Planet Exit Fuel Amount"
    )

    food_cnt: int = Field(
        description="Food Count"
    )

    sdu_cnt: int = Field(
        description="Sdu Count"
    )

    fuel_cnt: int = Field(
        description="Fuel Count"
    )

    ammo_cnt: int = Field(
        description="Ammo Count"
    )

    

