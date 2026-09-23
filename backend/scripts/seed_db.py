import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import AsyncSessionLocal, init_db
from app.services.seed_service import seed_demo_data


async def main():
    print("Initializing database tables...")
    await init_db()
    print("Seeding demo transaction bundles...")
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)
    print("Successfully seeded SkyView Residency, Prestige Palm, and Urban Greens bundles!")


if __name__ == "__main__":
    asyncio.run(main())
