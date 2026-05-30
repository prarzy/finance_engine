import asyncio
from sqlalchemy import inspect, text
from app.db.database import AsyncSessionLocal

async def check_tables():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        print("Tables in database:")
        for table in tables:
            print(f"  - {table}")
        
        # Check for key constraint tables
        constraint_tables = ['currencies', 'providers', 'provider_corridors', 'compliance_rules']
        missing = [t for t in constraint_tables if t not in tables]
        
        if missing:
            print(f"\nMissing tables: {missing}")
            print("Migrations NOT applied yet.")
            return False
        else:
            print("\nAll constraint tables present!")
            
            # Check if corridors are seeded
            result = await session.execute(text("SELECT COUNT(*) FROM provider_corridors"))
            count = result.scalar()
            print(f"Provider corridors seeded: {count} rows")
            
            if count > 0:
                print("Seeding ALREADY DONE.")
                return True
            else:
                print("Migrations applied but seeding NOT DONE yet.")
                return None

asyncio.run(check_tables())
