from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
from uuid import uuid4

class Entity(ABC):
    def __init__(self) -> None:
        self._id: str = str(uuid4())

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def summary(self) -> str:
        """Полиморфное описание для UI."""

class CatalogItem(Entity):
    def __init__(self, title: str) -> None:
        super().__init__()
        self._title = title
        self._available = True

    @property
    def title(self) -> str:
        return self._title

    @property
    def available(self) -> bool:
        return self._available

    def mark_issued(self) -> None:
        if not self._available:
            raise ValueError(f"«{self._title}» уже выдано")
        self._available = False

    def mark_returned(self) -> None:
        self._available = True

class Book(CatalogItem):
    def __init__(self, title: str, author: str, year: int) -> None:
        super().__init__(title)
        self._author = author
        self._year = year

    @property
    def author(self) -> str:
        return self._author

    @property
    def year(self) -> int:
        return self._year

    def summary(self) -> str:
        st = "в зале" if self.available else "на руках"
        return f"Книга: {self._author} — {self.title} ({self._year}) · {st}"

class Magazine(CatalogItem):
    def __init__(self, title: str, issue: int) -> None:
        super().__init__(title)
        self._issue = issue

    @property
    def issue(self) -> int:
        return self._issue

    def summary(self) -> str:
        st = "в зале" if self.available else "на руках"
        return f"Журнал: «{self.title}» №{self._issue} · {st}"

class Reader(Entity):
    def __init__(self, name: str, ticket: str) -> None:
        super().__init__()
        self._name = name
        self._ticket = ticket

    @property
    def name(self) -> str:
        return self._name

    @property
    def ticket(self) -> str:
        return self._ticket

    def summary(self) -> str:
        return f"{self._name} (билет {self._ticket})"

@dataclass
class Loan:
    item: CatalogItem
    reader: Reader
    due: date
    id: str = field(default_factory=lambda: str(uuid4()))
    returned: bool = False

    def is_overdue(self, today: Optional[date] = None) -> bool:
        today = today or date.today()
        return (not self.returned) and today > self.due

    def summary(self) -> str:
        if self.returned:
            flag = "возвращено"
        elif self.is_overdue():
            flag = "просрочено"
        else:
            flag = "активно"
        return f"{self.item.title} → {self.reader.name} до {self.due} ({flag})"