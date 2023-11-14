from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Cryptocurrency:
    ticker: str
    name: str
    circulating_supply: float
    max_supply: Optional[float] = None
    market_cap: float
    volume_24h: float
    change_24h: float 
    all_time_high: Optional[float] = None 
    all_time_low: Optional[float] = None

    @property
    def price(self) -> float:
        if self.circulating_supply > 0:
            return self.market_cap / self.circulating_supply
        else:
            return 0.0