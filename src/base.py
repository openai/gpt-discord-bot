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
    example_conversations: List[Conversation]


@dataclass(frozen=True)
class ThreadConfig:
    model: str
    max_tokens: int
    temperature: float


@dataclass(frozen=True)
class Prompt:
    header: Message
    examples: List[Conversation]
    convo: Conversation

    def full_render(self, bot_name):
        messages = [
            {
                "role": "system",
                "content": self.render_system_prompt(),
            }
        ]
        for message in self.render_messages(bot_name):
            messages.append(message)
        return messages

    def render_system_prompt(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [self.header.render()]
            + [Message("System", "Example conversations:").render()]
            + [conversation.render() for conversation in self.examples]
            + [
                Message(
                    "System", "Now, you will work with the actual current conversation."
                ).render()
            ]
        )

    def render_messages(self, bot_name):
        for message in self.convo.messages:
            if not bot_name in message.user:
                yield {
                    "role": "user",
                    "name": message.user,
                    "content": message.text,
                }
            else:
                yield {
                    "role": "assistant",
                    "name": bot_name,
                    "content": message.text,
                }
