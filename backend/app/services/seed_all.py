"""Master seed — imports all parts and seeds the database.
Run: python -m app.services.seed_all"""
import asyncio, json, sys, os
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.core.database import async_session, engine, Base
from app.models import WordPair

# Import all seed parts
from app.services.seed import SEED_JSON
from app.services.seed_food import SEED_PART2
from app.services.seed_transport import SEED_PART3
from app.services.seed_shopping import SEED_PART4
from app.services.seed_health import SEED_PART5
from app.services.seed_home_time import SEED_PART6
from app.services.seed_people import SEED_PART7
from app.services.seed_clothing_nature import SEED_PART8

def to_wordpair(w: dict) -> WordPair:
    return WordPair(
        estonian=w["estonian"],
        finnish=w["finnish"],
        estonian_example=w.get("et", ""),
        finnish_example=w.get("fi", ""),
        category=w.get("cat", "general"),
        is_cognate=bool(w.get("cog", 0)),
        difficulty=w.get("d", 1),
    )

async def seed_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        result = await db.execute(select(func.count(WordPair.id)))
        if result.scalar() > 0:
            print("⚠️  Database already seeded. Skipping.")
            return

        all_words = []

        # Part 1: from JSON in seed.py
        all_words.extend(json.loads(SEED_JSON))

        # Parts 2-8: from Python lists
        for part in [SEED_PART2, SEED_PART3, SEED_PART4, SEED_PART5,
                     SEED_PART6, SEED_PART7, SEED_PART8]:
            all_words.extend(part)

        # Deduplicate by (estonian, finnish) pair
        seen = set()
        unique = []
        for w in all_words:
            key = (w["estonian"], w["finnish"])
            if key not in seen:
                seen.add(key)
                unique.append(w)

        for w in unique:
            db.add(to_wordpair(w))

        await db.commit()
        print(f"✅ Seeded {len(unique)} unique word pairs!")

        # Print stats by category
        from sqlalchemy import text
        result = await db.execute(text(
            "SELECT category, COUNT(*) FROM word_pairs GROUP BY category ORDER BY COUNT(*) DESC"
        ))
        print("\n📊 Words by category:")
        for row in result:
            print(f"   {row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(seed_all())
