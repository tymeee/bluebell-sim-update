"""Shared API/local validation and allocation metadata."""
from typing import Literal
import math
from pydantic import BaseModel, Field, model_validator

INDEX_NAMES = [
    'US Equity', 'Thai Equity', 'China Equity', 'Bond/Fixed Income Fund',
    'Aggressive Mutual Fund', 'Moderate Mutual Fund', 'Conservative Mutual Fund',
    'Global Equity Fund', 'Healthcare Sector Fund', 'Technology Sector Fund',
    'Property/Real Estate Fund', 'Emerging Market Fund', 'Commodity Fund',
]
FUND_NAMES = ['KTPRECIOUS', 'ESGQG', 'ESEAE', 'ESGTECH', 'KKPGNPH', 'ESGCORE',
              'KKP Plus', 'KKP Cash', 'KFAFIX', 'UGISFX', 'KTHEALTHCAREA',
              'KFGPROPA', 'SCBS&P500A']
PRESETS = {
    'Bluebell Basic': {'KTHEALTHCAREA': .05, 'ESGTECH': .05, 'KFGPROPA': .05,
                      'KKP Plus': .35, 'KFAFIX': .30, 'UGISFX': .10, 'ESGCORE': .10},
    'Bluebell Balance': {'KTHEALTHCAREA': .05, 'ESGTECH': .05, 'KFGPROPA': .05,
                        'KKP Plus': .15, 'KFAFIX': .20, 'UGISFX': .10, 'ESEAE': .05,
                        'SCBS&P500A': .10, 'ESGCORE': .25},
    'Bluebell Beyond': {'KTHEALTHCAREA': .10, 'ESGTECH': .10, 'KFGPROPA': .10,
                       'KKP Plus': .05, 'KFAFIX': .05, 'UGISFX': .05, 'ESEAE': .10,
                       'SCBS&P500A': .10, 'ESGCORE': .35},
}

class SimulationRequest(BaseModel):
    model_config = {'extra': 'forbid', 'allow_inf_nan': False, 'validate_default': True}
    model: Literal['index', 'funds'] = 'index'
    age: int = Field(default=35, ge=0, le=84)
    years_until_retirement: int = Field(default=20, ge=0, le=84)
    initial_amount: float = Field(default=1_000_000, ge=0, le=100_000_000)
    monthly_contribution: float = Field(default=10_000, ge=0, le=300_000)
    annual_withdrawal: float = Field(default=100_000, ge=0, le=3_000_000)
    target: float = Field(default=5_000_000, ge=0, le=100_000_000)
    simulations: int = Field(default=250, ge=100, le=1000)
    inflation: float = Field(default=.02, ge=0, le=.15)
    weights: dict[str, float] = Field(default_factory=dict)
    seed: int | None = Field(default=None, ge=0, le=2**32 - 1)

    @model_validator(mode='after')
    def validate_portfolio(self):
        if self.age + self.years_until_retirement >= 85:
            raise ValueError('Retirement must begin before age 85.')
        allowed = set(INDEX_NAMES + ['Savings']) if self.model == 'index' else set(FUND_NAMES + ['Rostrum'])
        if set(self.weights) - allowed:
            raise ValueError('Unknown allocation name(s): ' + ', '.join(sorted(set(self.weights) - allowed)))
        if any(not math.isfinite(v) or v < 0 or v > 1 for v in self.weights.values()):
            raise ValueError('Each allocation must be finite and between 0 and 1.')
        if sum(self.weights.values()) > 1 + 1e-10:
            raise ValueError('Allocations exceed 100%.')
        if self.model == 'funds' and self.weights.get('Rostrum', 0) > 0:
            if self.initial_amount * self.weights['Rostrum'] < 3_000_000:
                raise ValueError('Rostrum requires an initial allocation of at least THB 3 million.')
        return self
