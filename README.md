# Chat-Server

To install and run... (ideally in a venv)

```bash
pip install -r requirements/release.txt
fastapi dev
```

## Development

For developing...

```bash
pip install -r requirements/dev.txt
```

We use [black](https://github.com/psf/black) for formatting and [mypy](https://github.com/python/mypy) to check types.


## Protocol
Server will assume that each websocket connection only has 1 user, so there is no need to specify sender ID. 

Each message in a conversation has a sequential ID, starting from 0.

Time is measured in milliseconds.

### Misc

#### `recv[user]`
Receive information about a user, happening at any time

```ts
client: { "type": "recv[user]", "user": user_id, "name": string, "desc": string }
```

#### `get[user]`
Get information about a user.

```ts
client: { "type": "get[user]", "user": user_id }
server: recv[user]
```

#### `set[user]`
Set information about yourself.

```ts
client: { "type": "set[user]", "name": string, "desc": string }
server: recv[user]
```

#### `update`
Get all new messages since the start time. There may be a large amount of them so these might be limited.

```ts
client: { "type": "update", "timestamp": number }
server: recv[direct]*
```

### Direct messaging

#### `recv[direct]`
Receive direct messages, happening at any time.

```ts
server: {
    "type": "recv[direct]", 
    "sender": user_id, 
    "recipient": user_id, 
    "content": string, 
    "timestamp": number, 
    "id": message_id 
}
```

#### `send[direct]`
Send direct messages to the server.

```ts
client: { "type": "send[direct]", "recipient": user_id, "content": string }
server: recv[direct]
```


#### `get[direct]`
Get a direct message from the past.

```ts
client: { "type": "get[direct]", "recipient": user_id, "id": message_id }
server: recv[direct]
```

### Group messaging
There is also a group messaging variant of some commands above.

TODO
