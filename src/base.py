from dataclasses import dataclass
from typing import Optional, List

SEPARATOR_TOKEN = "<|endoftext|>"


@dataclass(frozen=True)
class Message:
    user: str
    text: Optional[str] = None

    def render(self):
        result = self.user + ":"
        if self.text is not None:
            result += " " + self.text
        return result


@dataclass
class Conversation:
    messages: List[Message]

    def prepend(self, message: Message):
        self.messages.insert(0, message)
        return self

    def render(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [message.render() for message in self.messages]
        )


@dataclass(frozen=True)
class Config:
    name: str
    instructions: str


@dataclass(frozen=True)
class Prompt:
    header: Message
    convo: Conversation

    def render(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [self.header.render()]
            + [Message("System", "Current conversation:").render()]
            + [self.convo.render()],
        )
