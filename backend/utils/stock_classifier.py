class StockCategory:
    @staticmethod
    def is_etf(item: dict) -> bool:
        """
        判斷是否為 ETF：只要產業欄位中包含「ETF」關鍵字（不區分大小寫）
        """
        industry = item.get("industry_category", "")
        return "ETF" in industry.upper()

    @staticmethod
    def is_company_stock(item: dict) -> bool:
        """
        判斷是否為一般股票（排除 ETF、非數字 stock_id）
        """
        return (
            item.get("stock_id", "").isdigit() and
            not StockCategory.is_etf(item)
        )

    @staticmethod
    def is_index(item: dict) -> bool:
        """
        判斷是否為分類指數（非數字 stock_id，且非 ETF）
        """
        return (
            not item.get("stock_id", "").isdigit() and
            not StockCategory.is_etf(item)
        )

    @staticmethod
    def classify(item: dict) -> str:
        """
        回傳類型字串：'stock'、'etf'、'index'、'unknown'
        """
        if StockCategory.is_company_stock(item):
            return "stock"
        elif StockCategory.is_etf(item):
            return "etf"
        elif StockCategory.is_index(item):
            return "index"
        return "unknown"
