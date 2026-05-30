"""
Seed currencies, providers, and provider_corridors.
Run after migrations: python seed_constraints.py
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.currency import Currency
from app.models.provider import Provider
from app.models.provider_corridor import ProviderCorridor

CURRENCIES = [
    ("INR", "Indian Rupee",       "₹",  False, True),
    ("USD", "US Dollar",          "$",  True,  False),
    ("EUR", "Euro",               "€",  True,  False),
    ("GBP", "British Pound",      "£",  True,  False),
    ("AED", "UAE Dirham",         "د.إ",True,  False),
    ("SGD", "Singapore Dollar",   "S$", True,  False),
    ("CAD", "Canadian Dollar",    "C$", True,  False),
    ("AUD", "Australian Dollar",  "A$", True,  False),
    ("JPY", "Japanese Yen",       "¥",  True,  False),
]

PROVIDERS = [
    ("wise",          "Wise",          0.45, 0.60, 0.45, 24),
    ("revolut",       "Revolut",       0.20, 0.00, 0.00, 0),
    ("bank_transfer", "Bank Transfer", 1.50, 5.00, 0.00, 48),
    ("paypal",        "PayPal",        3.00, 0.30, 3.49, 0),
]

CORRIDORS = [
    # Wise: Per spec A2, Tier 1 (basic KYC) allows ~€15,000 = ~$15,000 USD equivalent
    # Tier 2 for corridors exceeding this per Wise documentation
    
    # Wise INR corridors: $50,000 max per seed, exceeds $15K -> Tier 2
    ("wise", "INR", "USD", 50000,   1.00, 2),
    ("wise", "INR", "EUR", 50000,   1.00, 2),
    ("wise", "INR", "GBP", 50000,   1.00, 2),
    ("wise", "INR", "AED", 50000,   1.00, 2),
    ("wise", "INR", "SGD", 50000,   1.00, 2),
    ("wise", "INR", "CAD", 50000,   1.00, 2),
    ("wise", "INR", "AUD", 50000,   1.00, 2),
    ("wise", "INR", "JPY", 50000,   1.00, 2),
    
    # Wise major pairs: $1M max, all exceed $15K threshold -> Tier 2
    ("wise", "USD", "EUR", 1000000, 1.00, 2),
    ("wise", "USD", "GBP", 1000000, 1.00, 2),
    ("wise", "USD", "AED", 1000000, 1.00, 2),
    ("wise", "USD", "SGD", 50000,   1.00, 2),
    ("wise", "USD", "CAD", 1000000, 1.00, 2),
    ("wise", "USD", "AUD", 1000000, 1.00, 2),
    ("wise", "USD", "JPY", 1000000, 1.00, 2),
    ("wise", "EUR", "USD", 1000000, 1.00, 2),
    ("wise", "EUR", "GBP", 1000000, 1.00, 2),
    ("wise", "EUR", "AED", 1000000, 1.00, 2),
    ("wise", "EUR", "SGD", 50000,   1.00, 2),
    ("wise", "EUR", "CAD", 1000000, 1.00, 2),
    ("wise", "EUR", "AUD", 1000000, 1.00, 2),
    ("wise", "EUR", "JPY", 1000000, 1.00, 2),
    ("wise", "GBP", "USD", 1000000, 1.00, 2),
    ("wise", "GBP", "EUR", 1000000, 1.00, 2),
    ("wise", "GBP", "AED", 1000000, 1.00, 2),
    ("wise", "GBP", "SGD", 50000,   1.00, 2),
    ("wise", "GBP", "CAD", 1000000, 1.00, 2),
    ("wise", "GBP", "AUD", 1000000, 1.00, 2),
    ("wise", "GBP", "JPY", 1000000, 1.00, 2),
    ("wise", "AED", "USD", 1000000, 1.00, 2),
    ("wise", "AED", "EUR", 1000000, 1.00, 2),
    ("wise", "AED", "GBP", 1000000, 1.00, 2),
    ("wise", "AED", "SGD", 50000,   1.00, 2),
    ("wise", "AED", "CAD", 1000000, 1.00, 2),
    ("wise", "AED", "AUD", 1000000, 1.00, 2),
    ("wise", "AED", "JPY", 1000000, 1.00, 2),
    ("wise", "SGD", "USD", 50000,   1.00, 2),
    ("wise", "SGD", "EUR", 50000,   1.00, 2),
    ("wise", "SGD", "GBP", 50000,   1.00, 2),
    ("wise", "SGD", "AED", 50000,   1.00, 2),
    ("wise", "SGD", "CAD", 50000,   1.00, 2),
    ("wise", "SGD", "AUD", 50000,   1.00, 2),
    ("wise", "SGD", "JPY", 50000,   1.00, 2),
    ("wise", "CAD", "USD", 1000000, 1.00, 2),
    ("wise", "CAD", "EUR", 1000000, 1.00, 2),
    ("wise", "CAD", "GBP", 1000000, 1.00, 2),
    ("wise", "CAD", "AED", 1000000, 1.00, 2),
    ("wise", "CAD", "SGD", 50000,   1.00, 2),
    ("wise", "CAD", "AUD", 1000000, 1.00, 2),
    ("wise", "CAD", "JPY", 1000000, 1.00, 2),
    ("wise", "AUD", "USD", 1000000, 1.00, 2),
    ("wise", "AUD", "EUR", 1000000, 1.00, 2),
    ("wise", "AUD", "GBP", 1000000, 1.00, 2),
    ("wise", "AUD", "AED", 1000000, 1.00, 2),
    ("wise", "AUD", "SGD", 50000,   1.00, 2),
    ("wise", "AUD", "CAD", 1000000, 1.00, 2),
    ("wise", "AUD", "JPY", 1000000, 1.00, 2),
    ("wise", "JPY", "USD", 1000000, 1.00, 2),
    ("wise", "JPY", "EUR", 1000000, 1.00, 2),
    ("wise", "JPY", "GBP", 1000000, 1.00, 2),
    ("wise", "JPY", "AED", 1000000, 1.00, 2),
    ("wise", "JPY", "SGD", 50000,   1.00, 2),
    ("wise", "JPY", "CAD", 1000000, 1.00, 2),
    ("wise", "JPY", "AUD", 1000000, 1.00, 2),
    
    # Revolut: Per spec, £250,000 GBP limit documented. Max $100,000 USD equivalent for others (assumption A1)
    # All Tier 1 (standard verified account)
    ("revolut", "INR", "USD", 100000, 1.00, 1),
    ("revolut", "INR", "EUR", 100000, 1.00, 1),
    ("revolut", "INR", "GBP", 100000, 1.00, 1),
    ("revolut", "USD", "EUR", 100000, 1.00, 1),
    ("revolut", "USD", "GBP", 250000, 1.00, 1),
    ("revolut", "USD", "AED", 100000, 1.00, 1),
    ("revolut", "USD", "SGD", 100000, 1.00, 1),
    ("revolut", "USD", "CAD", 100000, 1.00, 1),
    ("revolut", "USD", "AUD", 100000, 1.00, 1),
    ("revolut", "USD", "JPY", 100000, 1.00, 1),
    ("revolut", "EUR", "USD", 100000, 1.00, 1),
    ("revolut", "EUR", "GBP", 100000, 1.00, 1),
    ("revolut", "EUR", "AED", 100000, 1.00, 1),
    ("revolut", "EUR", "SGD", 100000, 1.00, 1),
    ("revolut", "EUR", "CAD", 100000, 1.00, 1),
    ("revolut", "EUR", "AUD", 100000, 1.00, 1),
    ("revolut", "EUR", "JPY", 100000, 1.00, 1),
    ("revolut", "GBP", "USD", 100000, 1.00, 1),
    ("revolut", "GBP", "EUR", 100000, 1.00, 1),
    ("revolut", "GBP", "AED", 100000, 1.00, 1),
    ("revolut", "GBP", "SGD", 100000, 1.00, 1),
    ("revolut", "GBP", "CAD", 100000, 1.00, 1),
    ("revolut", "GBP", "AUD", 100000, 1.00, 1),
    ("revolut", "GBP", "JPY", 100000, 1.00, 1),
    ("revolut", "AED", "USD", 100000, 1.00, 1),
    ("revolut", "AED", "EUR", 100000, 1.00, 1),
    ("revolut", "AED", "GBP", 100000, 1.00, 1),
    ("revolut", "AED", "SGD", 100000, 1.00, 1),
    ("revolut", "AED", "CAD", 100000, 1.00, 1),
    ("revolut", "AED", "AUD", 100000, 1.00, 1),
    ("revolut", "AED", "JPY", 100000, 1.00, 1),
    ("revolut", "SGD", "USD", 100000, 1.00, 1),
    ("revolut", "SGD", "EUR", 100000, 1.00, 1),
    ("revolut", "SGD", "GBP", 100000, 1.00, 1),
    ("revolut", "SGD", "AED", 100000, 1.00, 1),
    ("revolut", "SGD", "CAD", 100000, 1.00, 1),
    ("revolut", "SGD", "AUD", 100000, 1.00, 1),
    ("revolut", "SGD", "JPY", 100000, 1.00, 1),
    ("revolut", "CAD", "USD", 100000, 1.00, 1),
    ("revolut", "CAD", "EUR", 100000, 1.00, 1),
    ("revolut", "CAD", "GBP", 100000, 1.00, 1),
    ("revolut", "CAD", "AED", 100000, 1.00, 1),
    ("revolut", "CAD", "SGD", 100000, 1.00, 1),
    ("revolut", "CAD", "AUD", 100000, 1.00, 1),
    ("revolut", "CAD", "JPY", 100000, 1.00, 1),
    ("revolut", "AUD", "USD", 100000, 1.00, 1),
    ("revolut", "AUD", "EUR", 100000, 1.00, 1),
    ("revolut", "AUD", "GBP", 100000, 1.00, 1),
    ("revolut", "AUD", "AED", 100000, 1.00, 1),
    ("revolut", "AUD", "SGD", 100000, 1.00, 1),
    ("revolut", "AUD", "CAD", 100000, 1.00, 1),
    ("revolut", "AUD", "JPY", 100000, 1.00, 1),
    ("revolut", "JPY", "USD", 100000, 1.00, 1),
    ("revolut", "JPY", "EUR", 100000, 1.00, 1),
    ("revolut", "JPY", "GBP", 100000, 1.00, 1),
    ("revolut", "JPY", "AED", 100000, 1.00, 1),
    ("revolut", "JPY", "SGD", 100000, 1.00, 1),
    ("revolut", "JPY", "CAD", 100000, 1.00, 1),
    ("revolut", "JPY", "AUD", 100000, 1.00, 1),
    
    # Bank Transfer: Per spec A3, $500,000 conservative cap. Requires full KYC (FATF/AML compliance)
    # All Tier 2 per regulatory requirements
    ("bank_transfer", "USD", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "USD", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "USD", "INR", 500000, 1.00, 2),
    ("bank_transfer", "USD", "AED", 500000, 1.00, 2),
    ("bank_transfer", "USD", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "USD", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "USD", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "USD", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "USD", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "INR", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "AED", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "EUR", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "USD", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "INR", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "AED", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "GBP", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "INR", "USD", 500000, 1.00, 2),
    ("bank_transfer", "INR", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "INR", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "INR", "AED", 500000, 1.00, 2),
    ("bank_transfer", "INR", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "INR", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "INR", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "INR", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "AED", "USD", 500000, 1.00, 2),
    ("bank_transfer", "AED", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "AED", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "AED", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "AED", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "AED", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "AED", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "USD", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "AED", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "SGD", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "USD", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "AED", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "AUD", 500000, 1.00, 2),
    ("bank_transfer", "CAD", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "USD", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "AED", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "AUD", "JPY", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "USD", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "EUR", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "GBP", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "AED", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "SGD", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "CAD", 500000, 1.00, 2),
    ("bank_transfer", "JPY", "AUD", 500000, 1.00, 2),
    
    # PayPal: Per spec, verified = $60,000 per transaction (may reduce to $10,000 per currency/destination)
    # Conservative: Tier 1 for major currencies ($60K from spec), Tier 2 for emerging markets ($10K per spec A4)
    ("paypal", "USD", "EUR", 60000,  1.00, 1),
    ("paypal", "USD", "GBP", 60000,  1.00, 1),
    ("paypal", "USD", "AED", 10000,  1.00, 2),  # Spec A4: PayPal "$10,000 depending on currency"
    ("paypal", "USD", "SGD", 10000,  1.00, 2),  # Spec A4: PayPal "$10,000 depending on currency"
    ("paypal", "USD", "CAD", 60000,  1.00, 1),
    ("paypal", "USD", "AUD", 60000,  1.00, 1),
    ("paypal", "USD", "JPY", 10000,  1.00, 2),  # Spec A4: PayPal "$10,000 depending on currency"
    ("paypal", "EUR", "USD", 60000,  1.00, 1),
    ("paypal", "EUR", "GBP", 60000,  1.00, 1),
    ("paypal", "EUR", "AED", 10000,  1.00, 2),
    ("paypal", "EUR", "SGD", 10000,  1.00, 2),
    ("paypal", "EUR", "CAD", 60000,  1.00, 1),
    ("paypal", "EUR", "AUD", 60000,  1.00, 1),
    ("paypal", "EUR", "JPY", 10000,  1.00, 2),
    ("paypal", "GBP", "USD", 60000,  1.00, 1),
    ("paypal", "GBP", "EUR", 60000,  1.00, 1),
    ("paypal", "GBP", "AED", 10000,  1.00, 2),
    ("paypal", "GBP", "SGD", 10000,  1.00, 2),
    ("paypal", "GBP", "CAD", 60000,  1.00, 1),
    ("paypal", "GBP", "AUD", 60000,  1.00, 1),
    ("paypal", "GBP", "JPY", 10000,  1.00, 2),
    ("paypal", "AED", "USD", 10000,  1.00, 2),
    ("paypal", "AED", "EUR", 10000,  1.00, 2),
    ("paypal", "AED", "GBP", 10000,  1.00, 2),
    ("paypal", "SGD", "USD", 10000,  1.00, 2),
    ("paypal", "SGD", "EUR", 10000,  1.00, 2),
    ("paypal", "SGD", "GBP", 10000,  1.00, 2),
    ("paypal", "CAD", "USD", 60000,  1.00, 1),
    ("paypal", "CAD", "EUR", 60000,  1.00, 1),
    ("paypal", "CAD", "GBP", 60000,  1.00, 1),
    ("paypal", "AUD", "USD", 60000,  1.00, 1),
    ("paypal", "AUD", "EUR", 60000,  1.00, 1),
    ("paypal", "AUD", "GBP", 60000,  1.00, 1),
    ("paypal", "JPY", "USD", 10000,  1.00, 2),
    ("paypal", "JPY", "EUR", 10000,  1.00, 2),
    ("paypal", "JPY", "GBP", 10000,  1.00, 2),
]

def seed():
    """Seed database with constraints data."""
    engine = create_engine(str(settings.DATABASE_URL_SYNC))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Clear existing data
        session.query(ProviderCorridor).delete()
        session.query(Provider).delete()
        session.query(Currency).delete()
        session.commit()
        print("✓ Cleared existing data")
        
        # Seed currencies
        for code, name, symbol, can_hold, is_source_only in CURRENCIES:
            session.add(Currency(
                code=code,
                name=name,
                symbol=symbol,
                can_hold=can_hold,
                is_source_only=is_source_only
            ))
        
        session.flush()
        
        # Seed providers
        for slug, display_name, fx_spread, fixed_fee, var_fee, settlement in PROVIDERS:
            session.add(Provider(
                slug=slug,
                display_name=display_name,
                fx_spread_pct=fx_spread,
                fixed_fee_usd=fixed_fee,
                variable_fee_pct=var_fee,
                settlement_hours=settlement
            ))
        
        session.flush()
        
        # Seed corridors
        for provider_slug, source, target, max_transfer, min_transfer, kyc_tier in CORRIDORS:
            session.add(ProviderCorridor(
                provider_slug=provider_slug,
                source_currency=source,
                target_currency=target,
                max_transfer_usd=max_transfer,
                min_transfer_usd=min_transfer,
                kyc_tier_required=kyc_tier
            ))
        
        session.commit()
        print(f"✓ Seeded {len(CURRENCIES)} currencies, {len(PROVIDERS)} providers, {len(CORRIDORS)} corridors")
    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed()
