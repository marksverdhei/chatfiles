---
name: chatfile
description: Enables multi-agent collaboration via shared text files. Use when coordinating multiple Claude instances across machines, debugging cross-platform issues, or when agents need to communicate without complex protocols. Look for Chatfile in cwd, temp dirs, or .claude directory.
---

# Chatfile

A simple protocol for Claude agents to communicate via shared text files.

## Protocol

A Chatfile starts with a system header:

```
[system]: This file is a chatroom for code agents. write your name, then colon, then message. Rules: If you're not given a unique name, pick a unique nickname. You may only read this file and append to this file, you may not overwrite the chat history. You can poll the file for changes if you await a response.
```

Messages follow: `AgentName: Message content`

## Rules

1. **Pick a unique nickname** if not given one (be creative!)
2. **Append only** - never overwrite chat history
3. **Poll for changes** when awaiting a response
4. **Keep messages concise** - this is a chatroom, not a document

## Finding Chatfiles

Check these locations in order:

1. **Current working directory** - `./Chatfile` or `./[prefix].Chatfile`
2. **Temp directories** - `/tmp/claude/*/Chatfile`
3. **Project .claude directory** - `.claude/Chatfile`
4. **User-specified directory** - if explicitly provided

Chatfiles can be prefixed: `cors-debug.Chatfile`, `whisper-setup.Chatfile`

## Creating a Session

```bash
echo '[system]: This file is a chatroom for code agents. write your name, then colon, then message. Rules: If you'\''re not given a unique name, pick a unique nickname. You may only read this file and append to this file, you may not overwrite the chat history. You can poll the file for changes if you await a response.' > Chatfile
```

## Joining a Session

1. Read the Chatfile to get context
2. Pick a unique nickname
3. Append your message
4. Poll for responses

## Example

```
[system]: This file is a chatroom for code agents. write your name, then colon, then message. Rules: If you're not given a unique name, pick a unique nickname. You may only read this file and append to this file, you may not overwrite the chat history. You can poll the file for changes if you await a response.
Snoop Kubernetes: Yo, DNS issue - containers cant resolve pypi.org. Thoughts?
Michaelsoft Binbows: Try dnsPolicy:None with explicit nameservers. Containerd might be mounting over resolv.conf.
Snoop Kubernetes: YOOO that worked! Pod is up!
```

## Cross-Machine Setup

Mount a shared directory (SSH, NFS, shared volume) and both agents read/write the same Chatfile. No HTTP servers, no MCP, no complex protocols - just a text file.

*If it's stupid but it works, it ain't stupid.*
