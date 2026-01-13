# Two dumb solutions to agent orchestration that saved my life  

I was using the whisper service for the living room computer so my GPUs are free for experimentation and training.
But then the connection stopped working. I tried solving it with claude code on windows and on my main computer.
None could do it by themselves.

But then, what if they talk?

And then it struck me: 'i can just use a file'.


4 rules.

1. The file is Chatfile. Like dockerfile, prefix.Chatfile or simply Chatfile.
2. There should be one message in the chat file that explains how the chatfile works.
3. Syntax: `<name>: message\n`
4. One message, one line.
