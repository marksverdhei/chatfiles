#!/usr/bin/env python3
"""Scenic presentation intro screen."""

import subprocess
import sys
import re
from pathlib import Path

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Static
    from textual.containers import Center, Middle
    from textual.binding import Binding
except ImportError:
    print("Installing textual...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "textual", "-q"])
    from textual.app import App, ComposeResult
    from textual.widgets import Static
    from textual.containers import Center, Middle
    from textual.binding import Binding


def parse_chatfile(filepath: str) -> tuple[str, list[tuple[str, str]]]:
    """Parse a Chatfile and return (header, [(name, message), ...])."""
    content = Path(filepath).read_text()
    lines = content.strip().split('\n')

    # Find header (everything before first "Name: message" line)
    header_lines = []
    messages = []

    for line in lines:
        # Check if line matches "Name: message" pattern
        match = re.match(r'^([^:]+):\s*(.+)$', line)
        if match and not line.startswith('=') and not line.startswith('-') and not line.startswith(' '):
            name, msg = match.groups()
            # Skip if it looks like part of header
            if name.strip() in ['This file is a communication bridge between']:
                header_lines.append(line)
            else:
                messages.append((name.strip(), msg.strip()))
        else:
            if not messages:  # Still in header
                header_lines.append(line)

    return '\n'.join(header_lines), messages


def build_chatfile_slides(filepath: str, max_messages: int = 6) -> list[dict]:
    """Build slides from a Chatfile, one message per slide."""
    header, messages = parse_chatfile(filepath)

    # Truncate messages for presentation
    messages = messages[:max_messages]

    slides = []
    accumulated = []

    for i, (name, msg) in enumerate(messages):
        accumulated.append((name, msg))

        # Build the art: header (dim) + messages
        art_parts = [f"[dim cyan]{header}[/]\n"]

        for j, (n, m) in enumerate(accumulated):
            if j == len(accumulated) - 1:
                # Latest message: highlighted
                art_parts.append(f"\n[bold cyan]{n}:[/] [white]{m}[/]")
            else:
                # Previous messages: dimmed
                short_msg = m[:50] + "..." if len(m) > 50 else m
                art_parts.append(f"\n[dim white]{n}: {short_msg}[/]")

        is_last = i == len(messages) - 1
        slides.append({
            "art": ''.join(art_parts),
            "title": "[bold cyan]v0/Chatfile[/]",
            "body": f"\n[dim italic]Simple. Dumb. Works.[/]\n\n[dim]⏎  ENTER to continue[/]" if is_last else "\n\n[dim]⏎  ENTER to continue[/]",
        })

    return slides


LANDSCAPE = """[dim cyan]                    ·  ˚  ✦     ·  ˚        ✦    ·
              ✦         ·    ˚       ·   ✦      ˚     ·
                   ˚        ✦    ·        ˚   ·    ✦
        ·    ✦   ·     ˚        ·    ✦         ·      ˚[/]
[bold white]                                    ▲
                                   ▲▲▲
                                  ▲▲▲▲▲
                            ▲    ▲▲▲▲▲▲▲    ▲
                           ▲▲▲  ▲▲▲▲▲▲▲▲▲  ▲▲▲
                     ▲    ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲    ▲
                    ▲▲▲  ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲  ▲▲▲[/]
[dim white]▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄[/]
[dim green]░░▒▒░░░░▒▒░░░░░▒▒░░░░▒▒░░░░░▒▒░░░░▒▒░░░░░▒▒░░░░▒▒░░░░░▒▒░░░░▒▒░░░░░▒▒░░░░▒▒░░░[/]"""


SLIDES = [
    # Slide 0: The Problem
    {
        "art": """[cyan]
        ┌────────────┐                      ┌────────────┐
        │  WINDOWS   │         [bold]✗ ✗ ✗[/bold]       │  WHISPER   │
        │   Claude   │ ──────────────────▶ │  SERVICE   │
        └────────────┘     connection       └────────────┘
                             failed

        ┌────────────┐                      ┌────────────┐
        │    MAIN    │         [bold]✗ ✗ ✗[/bold]       │  WHISPER   │
        │   Claude   │ ──────────────────▶ │  SERVICE   │
        └────────────┘     connection       └────────────┘
                             failed[/]""",
        "title": "[bold cyan]The Problem[/]",
        "body": """
[white]I was using the whisper service for the living room computer
so my GPUs are free for experimentation and training.[/]

[bold cyan]But then the connection stopped working.[/]

[dim white]I tried solving it with Claude Code on Windows and on my main computer.
None could do it by themselves.[/]


[dim]⏎  ENTER to continue[/]""",
    },
    # Slide 2: The Revelation
    {
        "art": """[bold cyan]
                         ┌──────────────┐
                         │    CLAUDE    │
                         │    (win)     │
                         └──────┬───────┘
                                │
                                ▼
                        ┌───────────────┐
                        │   CHATFILE    │
                        └───────────────┘
                                ▲
                                │
                         ┌──────┴───────┐
                         │    CLAUDE    │
                         │    (main)    │
                         └──────────────┘[/]""",
        "title": "[bold cyan]But then, what if they talk?[/]",
        "body": """
[white]And then it struck me:[/]

[bold cyan]  'I can just use a file'  [/]


[dim]⏎  ENTER to continue[/]""",
    },
    # Slide 3: Rule 1
    {
        "art": """
[bold cyan]1.[/] [white]The file is [bold cyan]Chatfile[/white]
   [dim white]Like dockerfile: prefix.Chatfile or simply Chatfile[/]""",
        "title": "[bold cyan]4 Rules[/]",
        "body": """

[dim]⏎  ENTER to continue[/]""",
    },
    # Slide 4: Rule 2
    {
        "art": """
[bold cyan]1.[/] [white]The file is [bold cyan]Chatfile[/white]
   [dim white]Like dockerfile: prefix.Chatfile or simply Chatfile[/]

[bold cyan]2.[/] [white]One message explains how chatfile works[/]""",
        "title": "[bold cyan]4 Rules[/]",
        "body": """

[dim]⏎  ENTER to continue[/]""",
    },
    # Slide 5: Rule 3
    {
        "art": """
[bold cyan]1.[/] [white]The file is [bold cyan]Chatfile[/white]
   [dim white]Like dockerfile: prefix.Chatfile or simply Chatfile[/]

[bold cyan]2.[/] [white]One message explains how chatfile works[/]

[bold cyan]3.[/] [white]Syntax: [bold cyan]<name>: message[/][/]""",
        "title": "[bold cyan]4 Rules[/]",
        "body": """

[dim]⏎  ENTER to continue[/]""",
    },
    # Slide 6: Rule 4
    {
        "art": """
[bold cyan]1.[/] [white]The file is [bold cyan]Chatfile[/white]
   [dim white]Like dockerfile: prefix.Chatfile or simply Chatfile[/]

[bold cyan]2.[/] [white]One message explains how chatfile works[/]

[bold cyan]3.[/] [white]Syntax: [bold cyan]<name>: message[/][/]

[bold cyan]4.[/] [white]One message, one line[/]""",
        "title": "[bold cyan]4 Rules[/]",
        "body": """

[dim italic]Simple. Dumb. Works.[/]


[dim]⏎  ENTER to continue[/]""",
    },
    # Final Slide: Title
    {
        "art": LANDSCAPE,
        "title": """[bold bright_white]
 ██████╗██╗  ██╗ █████╗ ████████╗███████╗██╗██╗     ███████╗███████╗
██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔════╝██║██║     ██╔════╝██╔════╝
██║     ███████║███████║   ██║   █████╗  ██║██║     █████╗  ███████╗
██║     ██╔══██║██╔══██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
╚██████╗██║  ██║██║  ██║   ██║   ██║     ██║███████╗███████╗███████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝[/]""",
        "body": """
[bold cyan]Two dumb solutions to agent orchestration[/]
[dim white italic]that saved my life[/]


[dim]⏎  ENTER to launch demo[/]""",
    },
]

# Insert chatfile demo slides before the final title slide
CHATFILE_PATH = Path(__file__).parent / "v0" / "Chatfile"
if CHATFILE_PATH.exists():
    chatfile_slides = build_chatfile_slides(str(CHATFILE_PATH), max_messages=6)
    # Insert before last slide
    SLIDES = SLIDES[:-1] + chatfile_slides + [SLIDES[-1]]


class PresentationApp(App):
    """Scenic presentation."""

    CSS = """
    Screen {
        background: #0a0a12;
        align: center middle;
    }

    #content {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
    }

    .art {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
    }

    .title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
        margin-top: 1;
    }

    .body {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-align: center;
        margin-top: 1;
    }

    #counter {
        dock: bottom;
        height: 1;
        width: 100%;
        content-align: center middle;
        text-align: center;
        color: #555;
    }
    """

    BINDINGS = [
        Binding("enter", "next", "Next", show=False),
        Binding("space", "next", "Next", show=False),
        Binding("right", "next", "Next", show=False),
        Binding("left", "prev", "Previous", show=False),
        Binding("escape", "quit", "Quit", show=False),
        Binding("q", "quit", "Quit", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.slide_index = 0

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static(id="content")
        yield Static(id="counter")

    def on_mount(self) -> None:
        self.update_slide()

    def update_slide(self) -> None:
        slide = SLIDES[self.slide_index]
        content = f"{slide['art']}\n\n{slide['title']}\n{slide['body']}"
        self.query_one("#content", Static).update(content)
        self.query_one("#counter", Static).update(
            f"[dim]{self.slide_index + 1} / {len(SLIDES)}[/]"
        )

    def action_next(self) -> None:
        if self.slide_index < len(SLIDES) - 1:
            self.slide_index += 1
            self.update_slide()
        else:
            self.exit(result=True)

    def action_prev(self) -> None:
        if self.slide_index > 0:
            self.slide_index -= 1
            self.update_slide()

    def action_quit(self) -> None:
        self.exit(result=False)


def main():
    app = PresentationApp()
    result = app.run()

    if result:
        print("\n\033[1;36m✨ Launching Claude Code...\033[0m\n")
        subprocess.run(["claude"])


if __name__ == "__main__":
    main()
