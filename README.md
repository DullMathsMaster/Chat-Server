# Chat-Server

## Protocol
Server will assume that each websocket connection only has 1 user, so there is no need to specify sender ID. 

Each message in a conversation has a sequential ID, starting from 0.

Time is measured in milliseconds.

### `send[direct]`
For sending direct messages to the server.

```ts
send { "type": "send[direct]", "dest": user_id, "content": string }
recv { "type": "send[direct]", "id": user_id, "timestamp": number, "hash": string } // Not finalised
```

The response is necessary to verify that the message has arrived at the server.

### `recv[direct]`
When receiving direct messages, which happens any time.

```ts
recv { "type": "recv[direct]", "sender": user_id, "content": string, "timestamp": number, "id": message_id }
```

