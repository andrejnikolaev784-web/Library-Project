from datetime import date, timedelta

from models import Book, CatalogItem, Loan, Magazine, Reader
from repositories import InMemoryRepository, LoanStore

class LibraryService:
    LOAN_DAYS = 14

    def __init__(self) -> None:
        self._items = InMemoryRepository[CatalogItem]()
        self._readers = InMemoryRepository[Reader]()
        self._loans = LoanStore()
        self._seed()

    def _seed(self) -> None:
        self.add_book("Преступление и наказание", "Ф. М. Достоевский", 1866)
        self.add_book("Мастер и Маргарита", "М. А. Булгаков", 1967)
        self.add_magazine("Наука и жизнь", 3)
        self.add_reader("Анна Иванова", "A-101")
        self.add_reader("Пётр Сидоров", "B-202")

    def add_book(self, title: str, author: str, year: int) -> Book:
        book = Book(title.strip(), author.strip(), int(year))
        self._items.add(book)
        return book

    def add_magazine(self, title: str, issue: int) -> Magazine:
        mag = Magazine(title.strip(), int(issue))
        self._items.add(mag)
        return mag

    def add_reader(self, name: str, ticket: str) -> Reader:
        reader = Reader(name.strip(), ticket.strip())
        self._readers.add(reader)
        return reader

    def catalog(self) -> list[CatalogItem]:
        return self._items.all()

    def readers(self) -> list[Reader]:
        return self._readers.all()

    def loans(self) -> list[Loan]:
        return self._loans.all()

    def issue(self, item_id: str, reader_id: str) -> Loan:
        item = self._items.get(item_id)
        reader = self._readers.get(reader_id)
        if item is None:
            raise ValueError("Издание не найдено")
        if reader is None:
            raise ValueError("Читатель не найден")
        item.mark_issued()
        loan = Loan(
            item=item,
            reader=reader,
            due=date.today() + timedelta(days=self.LOAN_DAYS),
        )
        return self._loans.add(loan)

    def return_item(self, loan_id: str) -> Loan:
        loan = self._loans.get(loan_id)
        if loan is None:
            raise ValueError("Выдача не найдена")
        if loan.returned:
            raise ValueError("Уже возвращено")
        loan.returned = True
        loan.item.mark_returned()
        return loan