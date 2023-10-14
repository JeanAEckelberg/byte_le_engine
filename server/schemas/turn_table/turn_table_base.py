from pydantic import BaseModel


class TurnTableBase(BaseModel):
    turn_id: int
    turn_number: int
    run_id: int
    turn_data: str

    model_config: dict = {'from_attributes': True}
