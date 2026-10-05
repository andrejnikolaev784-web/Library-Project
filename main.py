import flet as ft
from abc import ABC, abstractmethod
from services import LibraryService
from theme import AppTheme

class PageView(ABC):
    """Базовый экран: все вкладки реализуют build()."""

    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        self._page = page
        self._library = library

    @abstractmethod
    def build(self) -> ft.Control:
        ...

    def refresh(self) -> None:
        self._page.update()

class CatalogPage(PageView):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        super().__init__(page, library)
        self._list = ft.Column(spacing=6)
        self._title = ft.TextField(label="Название", expand=True)
        self._author = ft.TextField(label="Автор", expand=True)
        self._year = ft.TextField(label="Год", width=100)
        self._issue = ft.TextField(label="№ журнала", width=120)

    def _reload(self) -> None:
        self._list.controls.clear()
        for item in self._library.catalog():
            self._list.controls.append(
                ft.ListTile(
                    title=ft.Text(item.summary()),
                    leading=ft.Icon(
                        ft.Icons.MENU_BOOK if item.available else ft.Icons.LOCK
                    ),
                )
            )

    def _add_book(self, _e: ft.ControlEvent) -> None:
        try:
            self._library.add_book(
                self._title.value or "",
                self._author.value or "",
                int(self._year.value or "0"),
            )
            self._title.value = self._author.value = self._year.value = ""
            self._reload()
            AppTheme.snack_ok(self._page, "Книга добавлена")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def _add_magazine(self, _e: ft.ControlEvent) -> None:
        try:
            self._library.add_magazine(
                self._title.value or "",
                int(self._issue.value or "0"),
            )
            self._title.value = self._issue.value = ""
            self._reload()
            AppTheme.snack_ok(self._page, "Журнал добавлен")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def build(self) -> ft.Control:
        self._reload()
        return ft.Column(
            [
                ft.Text("Каталог", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text(
                    "Для добавления книги укажите название, автора и год написания. Для добавления журнал укажите название и номер."
                ),
                ft.Row(
                    [
                        self._title,
                        self._author,
                        self._year,
                        ft.FilledButton("Книга", on_click=self._add_book),
                    ]
                ),
                ft.Row(
                    [
                        self._issue,
                        ft.OutlinedButton("Журнал (название сверху)", on_click=self._add_magazine),
                    ]
                ),
                ft.Divider(),
                self._list,
            ],
            spacing=AppTheme.GAP,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

class ReadersPage(PageView):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        super().__init__(page, library)
        self._list = ft.Column(spacing=6)
        self._name = ft.TextField(label="ФИО", expand=True)
        self._ticket = ft.TextField(label="Билет", width=160)

    def _reload(self) -> None:
        self._list.controls.clear()
        for r in self._library.readers():
            self._list.controls.append(ft.ListTile(title=ft.Text(r.summary())))

    def _add(self, _e: ft.ControlEvent) -> None:
        try:
            self._library.add_reader(self._name.value or "", self._ticket.value or "")
            self._name.value = self._ticket.value = ""
            self._reload()
            AppTheme.snack_ok(self._page, "Читатель зарегистрирован")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def build(self) -> ft.Control:
        self._reload()
        return ft.Column(
            [
                ft.Text("Читатели", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row(
                    [
                        self._name,
                        self._ticket,
                        ft.FilledButton("Добавить", on_click=self._add),
                    ]
                ),
                ft.Divider(),
                self._list,
            ],
            spacing=AppTheme.GAP,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

class LoansPage(PageView):
    def __init__(self, page: ft.Page, library: LibraryService) -> None:
        super().__init__(page, library)
        self._list = ft.Column(spacing=6)
        self._item_dd = ft.Dropdown(label="Издание", expand=True)
        self._reader_dd = ft.Dropdown(label="Читатель", expand=True)

    def _fill_dropdowns(self) -> None:
        self._item_dd.options = [
            ft.DropdownOption(key=item.id, text=item.summary())
            for item in self._library.catalog()
            if item.available
        ]
        self._reader_dd.options = [
            ft.DropdownOption(key=r.id, text=r.summary())
            for r in self._library.readers()
        ]

    def _reload_loans(self) -> None:
        self._list.controls.clear()
        for loan in self._library.loans():
            btn = ft.TextButton(
                "Вернуть",
                disabled=loan.returned,
                on_click=lambda e, lid=loan.id: self._return(lid),
            )
            self._list.controls.append(
                ft.ListTile(title=ft.Text(loan.summary()), trailing=btn)
            )

    def _issue(self, _e: ft.ControlEvent) -> None:
        try:
            if not self._item_dd.value or not self._reader_dd.value:
                raise ValueError("Выберите издание и читателя")
            self._library.issue(self._item_dd.value, self._reader_dd.value)
            self._item_dd.value = None
            self._fill_dropdowns()
            self._reload_loans()
            AppTheme.snack_ok(self._page, "Выдано на 14 дней")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def _return(self, loan_id: str) -> None:
        try:
            self._library.return_item(loan_id)
            self._fill_dropdowns()
            self._reload_loans()
            AppTheme.snack_ok(self._page, "Возвращено")
        except ValueError as exc:
            AppTheme.snack_err(self._page, str(exc))
        self.refresh()

    def build(self) -> ft.Control:
        self._fill_dropdowns()
        self._reload_loans()
        return ft.Column(
            [
                ft.Text("Выдачи", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row(
                    [
                        self._item_dd,
                        self._reader_dd,
                        ft.FilledButton("Выдать", on_click=self._issue),
                    ]
                ),
                ft.Divider(),
                self._list,
            ],
            spacing=AppTheme.GAP,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )


class LibraryApp:
    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._library = LibraryService()
        self._setup_page()

        loans = LoansPage(page, self._library).build()
        catalog = CatalogPage(page, self._library).build()
        readers = ReadersPage(page, self._library).build()

        self._tabs = ft.Tabs(
            length=3,
            selected_index=0,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Выдачи"),
                            ft.Tab(label="Каталог"),
                            ft.Tab(label="Читатели"),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[loans, catalog, readers],
                    ),
                ],
            ),
        )

    def _setup_page(self) -> None:
        self._page.title = "Библиотека"
        self._page.padding = AppTheme.PAGE_PADDING
        self._page.theme_mode = ft.ThemeMode.LIGHT

    def run(self) -> None:
        self._page.add(self._tabs)

def main(page: ft.Page) -> None:
    LibraryApp(page).run()

if __name__ == "__main__":
    ft.run(main)