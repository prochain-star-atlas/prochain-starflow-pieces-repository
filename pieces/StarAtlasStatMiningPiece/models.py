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

    planet_name: str = Field(
        default="",
        description="Planet Name",
    )

    location_x: int = Field(
        description="location_x"
    )

    location_y: int = Field(
        description="location_y"
    )

    food_consumption_rate: float = Field(
        description="food_consumption_rate"
    )

    ammo_consumption_rate: float = Field(
        description="ammo_consumption_rate"
    )

    mining_rate: float = Field(
        description="mining_rate"
    )

    max_mining_duration: float = Field(
        description="max_mining_duration"
    )

    mine_time_passed: float = Field(
        description="mine_time_passed"
    )

    mine_time_in_minutes_passed: float = Field(
        description="mine_time_in_minutes_passed"
    )

    food_consumed: float = Field(
        description="food_consumed"
    )

    ammo_consumed: float = Field(
        description="ammo_consumed"
    )

    resource_mined: float = Field(
        description="resource_mined"
    )

    time_food_remaining: float = Field(
        description="time_food_remaining"
    )

    time_food_in_minutes_remaining: float = Field(
        description="time_food_in_minutes_remaining"
    )

    time_ammo_remaining: float = Field(
        description="time_ammo_remaining"
    )

    time_ammo_in_minutes_remaining: float = Field(
        description="time_ammo_in_minutes_remaining"
    )

    sim_current_cargo: float = Field(
        description="sim_current_cargo"
    )

    time_cargo_remaining: float = Field(
        description="time_cargo_remaining"
    )

    time_cargo_in_minutes_remaining: float = Field(
        description="time_cargo_in_minutes_remaining"
    )

    time_limit: float = Field(
        description="time_limit"
    )

    time_limit_in_minutes: float = Field(
        description="time_limit_in_minutes"
    )

    mine_end: float = Field(
        description="mine_end"
    )

    mine_end_string: float = Field(
        description="mine_end_string"
    )

    mine_end_iso_string: float = Field(
        description="mine_end_iso_string"
    )

    sage_resource_mined: float = Field(
        description="sage_resource_mined"
    )

    system_richness: float = Field(
        description="system_richness"
    )

    resource_hardness: float = Field(
        description="resource_hardness"
    )

