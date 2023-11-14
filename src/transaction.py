from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: datetime
    transaction_fee: float
    block_number: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "transaction_fee": self.transaction_fee,
            "block_number": self.block_number
        }
