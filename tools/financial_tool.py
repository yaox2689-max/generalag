import akshare as ak

from tools.base import BaseTool, ToolResult


class FinancialTool(BaseTool):
    name = "financial_report"
    description = (
        "Query financial report data for Chinese A-share listed companies via AKShare. "
        "Supports: income statement (利润表), balance sheet (资产负债表), cash flow (现金流量表)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol, e.g. '600519' for 贵州茅台",
            },
            "report_type": {
                "type": "string",
                "description": "Report type: 'income' (利润表), 'balance' (资产负债表), 'cashflow' (现金流量表)",
                "enum": ["income", "balance", "cashflow"],
            },
            "period": {
                "type": "string",
                "description": "Report period in YYYYMMDD format, e.g. '20240930' for 2024 Q3. Omit for latest.",
            },
        },
        "required": ["symbol", "report_type"],
    }

    _report_map = {
        "income": ak.stock_financial_report_sina,
        "balance": ak.stock_financial_report_sina,
        "cashflow": ak.stock_financial_report_sina,
    }

    _category_map = {
        "income": "利润表",
        "balance": "资产负债表",
        "cashflow": "现金流量表",
    }

    async def execute(self, symbol: str, report_type: str, period: str = "", **kwargs) -> ToolResult:
        try:
            category = self._category_map[report_type]
            df = ak.stock_financial_report_sina(stock=symbol, symbol=category)

            if df is None or df.empty:
                return ToolResult(success=False, output="", error=f"No data found for {symbol}")

            if period:
                # Try to filter by period column
                date_col = None
                for col in df.columns:
                    if "日期" in col or "报告" in col or "date" in col.lower():
                        date_col = col
                        break
                if date_col:
                    df = df[df[date_col].astype(str).str.contains(period)]

            # Limit to most recent 3 rows, select key columns to avoid token explosion
            df = df.head(3)
            # Use first column (date) + every 3rd column to keep output compact
            cols = list(df.columns)
            selected = [cols[0]] + cols[1::3]
            df_slim = df[selected]

            lines = []
            for _, row in df_slim.iterrows():
                items = [f"{col}: {row[col]}" for col in df_slim.columns]
                lines.append(" | ".join(items))
            output = "\n".join(lines)

            return ToolResult(
                success=True,
                output=f"## {symbol} {category}\n\n{output}",
                metadata={"rows": len(df), "report_type": report_type},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
