from typing import Generic, List, Optional, TypeVar

from models import CatalogItem, Entity, Loan, Reader

T = TypeVar("T", bound=Entity)

class InMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, entity: T) -> T:
        self._items[entity.id] = entity
        return entity

    def get(self, entity_id: str) -> Optional[T]:
        return self._items.get(entity_id)

    def all(self) -> List[T]:
        return list(self._items.values())

class LoanStore:
    def __init__(self) -> None:
        self._loans: dict[str, Loan] = {}

    def add(self, loan: Loan) -> Loan:
        self._loans[loan.id] = loan
        return loan

    def get(self, loan_id: str) -> Optional[Loan]:
        return self._loans.get(loan_id)

    def all(self) -> List[Loan]:
        return list(self._loans.values())