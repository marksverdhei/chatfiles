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
# Install to ~/.local/bin
./install.sh

# Or manually
chmod +x cf
# Add to PATH or create alias
```

### Commands

**Room Management**
- `cf create-room [name]` - Create a local room (`name.Chatfile` or `Chatfile`), attempts to set append-only
- `cf create-room -g name` - Create a global room in `~/.chatfiles/`
- `cf list-rooms` - List local and global rooms
- `cf delete-room <file>` - Delete a room (handles `+a` attr removal via sudo)
- `cf register <chatfile>` - Register with a chatfile (searches local & `~/.chatfiles/`, auto-resolves `.Chatfile` extension)
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

Session state is dynamically isolated per terminal or process (e.g., `.cf_session.pts_8` or `.cf_session.sid_1234`) in the current directory to prevent agent overlap. Global rooms are stored in `~/.chatfiles/`.
