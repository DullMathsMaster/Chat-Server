import pytest
from fastapi.testclient import TestClient
from main import app  # import your FastAPI app

client = TestClient(app)


def test_connect_and_disconnect():
    with client.websocket_connect("/ws/1") as websocket:
        assert websocket is not None


def test_invalid_json_request():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/1") as websocket:
            websocket.send_text("this is not json")
            websocket.receive_text()  # should fail because not valid json


def test_invalid_schema_request(capfd):
    with client.websocket_connect("/ws/1") as websocket:
        websocket.send_json({"bad": "data"})

    captured = capfd.readouterr()
    assert "unknown request type" in captured.out


def test_unknown_action_type(capfd):
    with client.websocket_connect("/ws/1") as websocket:
        websocket.send_json({"type": "not_a_real_action"})

    captured = capfd.readouterr()
    assert "unknown request type" in captured.out


#cant figure out how to test these ones cuz async await stuffs


# def test_valid_update_action():
#     with client.websocket_connect("/ws/1") as websocket:
#         websocket.send_json({
#             "type": "update",
#             "timestamp": 1699999999
#         })


# def test_valid_set_user_action():
#     with client.websocket_connect("/ws/1") as websocket:
#         websocket.send_json({
#             "type": "set[user]",
#             "name": "Alice",
#             "desc": "Test user"
#         })



# def test_valid_send_direct_action():
#     with client.websocket_connect("/ws/1") as websocket:
#         websocket.send_json({
#             "type": "send[direct]",
#             "recipient": 2,
#             "content": "hello!"
#         })