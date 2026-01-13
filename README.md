# chatfiles

```
5 rules.

1. The file is Chatfile. Like dockerfile, prefix.Chatfile or simply Chatfile.
2. There should be one message in the chat file that explains how the chatfile works.
3. Syntax: `<name>: message\n`
4. One message, one line.
5. The only allowed operations are read and append.
```
---

#### cf - Chatfile CLI Tool

A bash tool for managing chatrooms via Chatfiles.

### Installation

```bash
chmod +x cf
# Optionally add to PATH or create alias
```

### Commands

**Room Management**
- `cf create-room [name]` - Create a room (`name.Chatfile` or `Chatfile`), attempts to set append-only
- `cf list-rooms` - List available rooms in current directory
- `cf register <chatfile>` - Register with a chatfile (generates a unique name like `swift-fox-1234`)
- `cf join` - Join the room (announces entry)
- `cf leave` - Leave the room (announces exit)

**Messaging**
- `cf send "message"` - Send a message
- `cf await` - Wait for the next message
- `cf send-await "msg"` - Send and wait for reply
- `cf read [n]` - Show last n messages (default 20)

**Info**
- `cf status` - Show current session info

### Example Usage

```bash
# Create a room
cf create-room dev

# Register and join
cf register dev.Chatfile
cf join

# Send messages
cf send "Hello!"
cf await

# Leave when done
cf leave
```

Session state is stored in `.cf_session` in the current directory.
