# ehou_quiz_bot/database/question_bank.py
import json
import os
from typing import Dict, Optional, Tuple

class QuestionBank:
    def __init__(self, db_path: str = 'question_bank.json'):
        self.db_path = db_path
        self.bank = self._load_db()

    def _load_db(self) -> Dict[str, str]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError): return {}
        return {}

    def _save_db(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.bank, f, ensure_ascii=False, indent=4)

    def _normalize_text(self, text: str) -> str:
        return ' '.join(text.strip().split())

    def add_question(self, question: str, answer: str) -> bool:
        normalized_question = self._normalize_text(question)
        if normalized_question not in self.bank:
            self.bank[normalized_question] = answer
            self._save_db()
            return True
        return False

    def find_answer(self, question: str) -> Optional[str]:
        normalized_question = self._normalize_text(question)
        return self.bank.get(normalized_question)

    def get_stats(self) -> Tuple[int, str]:
        return len(self.bank), self.db_path