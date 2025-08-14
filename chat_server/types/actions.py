from pydantic import BaseModel, ConfigDict

__all__ = ["Action", "action_models"]




class Action(BaseModel):
    model_config = ConfigDict(strict=True)
    type: str


class Update(Action):
    timestamp: int


class RecvUser(Action):
    user: int
    name: str
    desc: str


class GetUser(Action):
    user: int


class SetUser(Action):
    name: str
    desc: str


class RecvDirect(Action):
    sender: int
    recipient: int
    content: str
    timestamp: int
    seq_no: int


class GetDirect(Action):
    recipient: int
    seq_no: int


class SendDirect(Action):
    recipient: int
    content: str



action_models = {
    "Update": Update,
    "RecvUser": RecvUser,
    "GetUser": GetUser,
    "SetUser": SetUser,
    "RecvDirect": RecvDirect,
    "GetDirect": GetDirect,
    "SendDirect": SendDirect,
}