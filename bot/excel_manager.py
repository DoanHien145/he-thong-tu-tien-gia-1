from bot.db_manager import DatabaseManager

class ExcelManager(DatabaseManager):
    """
    ExcelManager is now a backward-compatible wrapper around SQLite DatabaseManager.
    All data is stored persistently in SQLite (data/cultivation.db).
    """
    def __init__(self, excel_path: str = "data/data.xlsx"):
        db_path = excel_path.replace(".xlsx", ".db")
        if not db_path.endswith(".db"):
            db_path = "data/cultivation.db"
        super().__init__(db_path=db_path)
        self.excel_path = excel_path

    async def save(self):
        """Export SQLite data to Excel file for web downloads."""
        await self.export_to_excel(self.excel_path)
