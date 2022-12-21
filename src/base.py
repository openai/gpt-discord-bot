from dataclasses import dataclass
from typing import Optional

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
    messages: list[Message]

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
    example_conversations: list[Conversation]


@dataclass(frozen=True)
class Prompt:
    header: Message
    examples: list[Conversation]
    convo: Conversation

    def render(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [self.header.render()]
            + [Message("System", "Example conversations:").render()]
            + [conversation.render() for conversation in self.examples]
            + [Message("System", "Current conversation:").render()]
            + [self.convo.render()],
        )
