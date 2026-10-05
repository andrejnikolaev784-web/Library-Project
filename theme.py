class AppTheme:
    PAGE_PADDING = 16
    GAP = 12

    @staticmethod
    def _snack(page: ft.Page, text: str, color) -> None:
        bar = ft.SnackBar(content=ft.Text(text), bgcolor=color)
        # убрать предыдущие SnackBar, остальное в overlay не трогать
        page.overlay[:] = [c for c in page.overlay if not isinstance(c, ft.SnackBar)]
        page.overlay.append(bar)
        bar.open = True
        page.update()

    @staticmethod
    def snack_ok(page: ft.Page, text: str) -> None:
        AppTheme._snack(page, text, ft.Colors.GREEN_700)

    @staticmethod
    def snack_err(page: ft.Page, text: str) -> None:
        AppTheme._snack(page, text, ft.Colors.RED_700)