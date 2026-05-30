"""Corridor and provider management endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    CorridorOut,
    CurrencyOut,
    LimitCheckResult,
    SupportedRoutesResponse,
    TransferLimitCheckRequest,
    TransferLimitCheckResponse,
)
from app.db.database import get_db
from app.services.constraint_service import constraint_service
from app.core.exceptions import BadRequestError

router = APIRouter()


@router.post("/check-limits", response_model=TransferLimitCheckResponse)
async def check_transfer_limits(
    request: TransferLimitCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> TransferLimitCheckResponse:
    """
    Check if an amount is valid for multiple provider corridors.
    Returns per-provider validation results.
    """
    source = request.source_currency.upper()
    target = request.target_currency.upper()
    
    results = []
    any_valid = False
    
    for provider_slug in request.methods:
        provider = provider_slug.lower()
        corridor = constraint_service.get_constraint(provider, source, target)
        
        if corridor is None:
            results.append(LimitCheckResult(
                provider=provider,
                valid=False,
                error=f"Corridor not supported",
                max_transfer_usd=None,
            ))
            continue
        
        # Check amount limits
        if request.amount < corridor.min_transfer_usd:
            results.append(LimitCheckResult(
                provider=provider,
                valid=False,
                error=f"Below minimum: ${corridor.min_transfer_usd:.2f}",
                max_transfer_usd=corridor.max_transfer_usd,
            ))
            continue
        
        if (
            corridor.max_transfer_usd is not None
            and request.amount > corridor.max_transfer_usd
        ):
            results.append(LimitCheckResult(
                provider=provider,
                valid=False,
                error=f"Exceeds maximum: ${corridor.max_transfer_usd:.2f}",
                max_transfer_usd=corridor.max_transfer_usd,
            ))
            continue
        
        # Amount is valid for this provider
        results.append(LimitCheckResult(
            provider=provider,
            valid=True,
            error=None,
            max_transfer_usd=corridor.max_transfer_usd,
        ))
        any_valid = True
    
    return TransferLimitCheckResponse(
        results=results,
        any_valid=any_valid,
        amount_usd=request.amount,
    )


@router.get("/corridors", response_model=SupportedRoutesResponse)
async def get_supported_corridors(
    db: AsyncSession = Depends(get_db),
) -> SupportedRoutesResponse:
    """
    Get all supported payment corridors grouped by provider.
    Returns currencies and corridors for route planning UI.
    """
    # Get all corridors grouped by provider
    corridors_by_provider = constraint_service.get_all_corridors_grouped()

    # Convert to response format
    provider_corridors = {}
    for provider_slug, corridors in corridors_by_provider.items():
        provider_corridors[provider_slug] = [
            CorridorOut(
                provider_slug=c.provider_slug,
                source_currency=c.source_currency,
                target_currency=c.target_currency,
                max_transfer_usd=c.max_transfer_usd,
                min_transfer_usd=c.min_transfer_usd,
                kyc_tier_required=c.kyc_tier_required,
                settlement_hours=24,  # Default, could be enhanced per provider
            )
            for c in corridors
        ]

    # Get unique currencies from all corridors
    currencies_set = set()
    for corridors in corridors_by_provider.values():
        for c in corridors:
            currencies_set.add(c.source_currency)
            currencies_set.add(c.target_currency)

    # For now, return basic currency info (will be enhanced with DB lookup)
    currencies = [
        CurrencyOut(
            code=code,
            name=code,  # Placeholder
            symbol="$",  # Placeholder
            can_hold=True,
            is_source_only=False,
        )
        for code in sorted(currencies_set)
    ]

    return SupportedRoutesResponse(
        currencies=currencies,
        corridors_by_provider=provider_corridors,
    )
