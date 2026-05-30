"""
ConstraintService — loads provider corridors from DB and answers validity queries.
All corridor data is loaded at startup and cached in-memory (refreshable).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.provider_corridor import ProviderCorridor
from app.models.provider import Provider
import logging

logger = logging.getLogger(__name__)


@dataclass
class CorridorConstraint:
    provider_slug: str
    source_currency: str
    target_currency: str
    max_transfer_usd: Optional[float]
    min_transfer_usd: float
    kyc_tier_required: int


class ConstraintService:
    """
    In-memory cache of all valid corridors.
    Keyed as: (provider_slug, source_currency, target_currency) -> CorridorConstraint
    """

    def __init__(self):
        self._corridors: dict[tuple, CorridorConstraint] = {}
        self._providers: dict[str, dict] = {}

    async def load(self, session: AsyncSession) -> None:
        """Load all active corridors and providers from DB into memory."""
        result = await session.execute(
            select(ProviderCorridor).where(ProviderCorridor.is_active == True)
        )
        corridors = result.scalars().all()
        self._corridors = {
            (c.provider_slug, c.source_currency, c.target_currency): CorridorConstraint(
                provider_slug=c.provider_slug,
                source_currency=c.source_currency,
                target_currency=c.target_currency,
                max_transfer_usd=float(c.max_transfer_usd) if c.max_transfer_usd else None,
                min_transfer_usd=float(c.min_transfer_usd),
                kyc_tier_required=c.kyc_tier_required,
            )
            for c in corridors
        }
        prov_result = await session.execute(
            select(Provider).where(Provider.is_active == True)
        )
        self._providers = {
            p.slug: {
                "display_name": p.display_name,
                "fx_spread_pct": float(p.fx_spread_pct),
                "fixed_fee_usd": float(p.fixed_fee_usd),
                "variable_fee_pct": float(p.variable_fee_pct),
                "settlement_hours": p.settlement_hours,
            }
            for p in prov_result.scalars().all()
        }
        logger.info(f"ConstraintService loaded {len(self._corridors)} corridors, {len(self._providers)} providers")

    def is_valid_corridor(
        self,
        provider_slug: str,
        source_currency: str,
        target_currency: str,
        kyc_tier: int = 1,
    ) -> bool:
        key = (provider_slug, source_currency, target_currency)
        if key not in self._corridors:
            return False
        return self._corridors[key].kyc_tier_required <= kyc_tier

    def get_constraint(
        self, provider_slug: str, source_currency: str, target_currency: str
    ) -> Optional[CorridorConstraint]:
        return self._corridors.get((provider_slug, source_currency, target_currency))

    def get_valid_corridors_for_pair(
        self, source_currency: str, target_currency: str, kyc_tier: int = 1
    ) -> list[CorridorConstraint]:
        return [
            c for (p, s, t), c in self._corridors.items()
            if s == source_currency and t == target_currency and c.kyc_tier_required <= kyc_tier
        ]

    def get_provider_cost_config(self, provider_slug: str) -> Optional[dict]:
        return self._providers.get(provider_slug)

    def validate_amount_for_corridor(
        self,
        provider_slug: str,
        source_currency: str,
        target_currency: str,
        amount_usd: float,
    ) -> tuple[bool, Optional[str]]:
        """
        Returns (is_valid, error_message_or_None).
        """
        c = self.get_constraint(provider_slug, source_currency, target_currency)
        if c is None:
            return False, f"{provider_slug} does not support {source_currency}→{target_currency}"
        if amount_usd < c.min_transfer_usd:
            return False, f"Minimum transfer for {provider_slug} on this corridor is ${c.min_transfer_usd:.2f}"
        if c.max_transfer_usd is not None and amount_usd > c.max_transfer_usd:
            return False, f"Maximum transfer for {provider_slug} on this corridor is ${c.max_transfer_usd:,.2f}"
        return True, None

    def get_all_corridors_grouped(self) -> dict[str, list[CorridorConstraint]]:
        """Returns corridors grouped by provider_slug, for the Supported Routes page."""
        grouped: dict[str, list] = {}
        for c in self._corridors.values():
            grouped.setdefault(c.provider_slug, []).append(c)
        return grouped


# Singleton — instantiated in app startup
constraint_service = ConstraintService()
