import json
from typing import List, Dict
from datetime import datetime
import os
import uuid

from src.models.portfolio import PortfolioHolding, Transaction

PORTFOLIO_FILE = "data/portfolio_holdings.json"
TRANSACTIONS_FILE = "data/transactions.json"

class PortfolioService:
    def __init__(self):
        self._ensure_data_files_exist()

    def _ensure_data_files_exist(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "w") as f:
                json.dump({"holdings": [], "last_updated": str(datetime.now())}, f, indent=2)
        if not os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, "w") as f:
                json.dump({"transactions": []}, f, indent=2)

    def _read_data(self, file_path: str) -> Dict:
        with open(file_path, "r") as f:
            return json.load(f)

    def _write_data(self, file_path: str, data: Dict):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def get_holdings(self) -> List[PortfolioHolding]:
        data = self._read_data(PORTFOLIO_FILE)
        return [PortfolioHolding(**h) for h in data.get("holdings", [])]

    def add_holding(self, holding: PortfolioHolding) -> PortfolioHolding:
        data = self._read_data(PORTFOLIO_FILE)
        data["holdings"].append(holding.model_dump())
        data["last_updated"] = datetime.now()
        self._write_data(PORTFOLIO_FILE, data)
        return holding

    def get_transactions(self) -> List[Transaction]:
        data = self._read_data(TRANSACTIONS_FILE)
        return [Transaction(**t) for t in data.get("transactions", [])]

    def add_transaction(self, holding: PortfolioHolding) -> Transaction:
        transaction = Transaction(
            id=str(uuid.uuid4()),
            date=datetime.now(),
            type="buy",
            symbol=holding.symbol,
            shares=holding.shares,
            price=holding.purchase_price,
            total=holding.shares * holding.purchase_price,
            notes=holding.notes,
        )
        data = self._read_data(TRANSACTIONS_FILE)
        data["transactions"].append(transaction.model_dump())
        self._write_data(TRANSACTIONS_FILE, data)
        return transaction 