# Chat-Server

## Protocol
Server will assume that each websocket connection only has 1 user, so there is no need to specify sender ID. 

Each message in a conversation has a sequential ID, starting from 0.

Time is measured in milliseconds.

### Misc

#### `get[user]`
Get information about a user.

```ts
client: { "type": "get[user]", "user": user_id }
server: { "type": "get[user]", "user": user_id, "name": string, "desc": string }
```

#### `set[user]`
Set information about yourself.

```ts
client: { "type": "set[user]", "name": string, "desc": string }
server: { "type": "set[user]", "name": string, "desc": string }
```

#### `update`
Get all new messages since the start time. There may be a large amount of them so these might be limited.

```ts
client: { "type": "update", "timestamp": number }
server: recv[direct]*
```

### Direct messaging

#### `send[direct]`
Send direct messages to the server.

```ts
client: { "type": "send[direct]", "dest_id": user_id, "content": string }
server: recv[direct]
```

#### `recv[direct]`
Receive direct messages, happening at any time.

```ts
server: { "type": "recv[direct]", "sender": user_id, "content": string, "timestamp": number, "id": message_id }
```

#### `get[direct]`
Get a direct message from the past, by replaying `recv`.

```ts
client: { "type": "get[direct]", "dest_id": user_id, "id": message_id }
server: recv[direct]
```

### Group messaging
There is also a group messaging variant of some commands above.

TODO

