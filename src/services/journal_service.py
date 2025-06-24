import json
from typing import List, Dict
import os
from datetime import datetime

from src.models.journal import JournalEntry

JOURNAL_FILE = "data/journal.json"

class JournalService:
    def __init__(self):
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(JOURNAL_FILE):
            with open(JOURNAL_FILE, "w") as f:
                json.dump({"entries": []}, f, indent=2)

    def _read_data(self) -> Dict:
        with open(JOURNAL_FILE, "r") as f:
            return json.load(f)

    def _write_data(self, data: Dict):
        with open(JOURNAL_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def get_entries(self) -> List[JournalEntry]:
        data = self._read_data()
        return [JournalEntry(**entry) for entry in data.get("entries", [])]

    def add_entry(self, entry: JournalEntry) -> JournalEntry:
        data = self._read_data()
        data["entries"].append(entry.model_dump())
        # Sort entries by date, newest first
        data["entries"] = sorted(data["entries"], key=lambda x: x['date'], reverse=True)
        self._write_data(data)
        return entry 