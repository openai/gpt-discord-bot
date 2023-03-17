from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Message:
    user: str
    text: Optional[str] = None

    def render(self):
        result = {"role": self.user, "content": self.text}
        return result
