"""Quick seed — bypasses checks and commits in batches."""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sqlalchemy import text
from app.core.database import engine, Base, async_session
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
from app.services.seed_extra import SEED_PART9
from app.services.seed_verbs import SEED_PART10
from app.services.seed_1000 import SEED_PART12

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

async def seed_quick():
    # Drop and recreate
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS srs_cards"))
        await conn.execute(text("DROP TABLE IF EXISTS user_progress"))
        await conn.execute(text("DROP TABLE IF EXISTS word_pairs"))
        await conn.execute(text("DROP TABLE IF EXISTS users"))
        await conn.run_sync(Base.metadata.create_all)
    
    # Collect all words
    all_words = []
    all_words.extend(json.loads(SEED_JSON))
    all_words.extend(SEED_PART2)
    all_words.extend(SEED_PART3)
    all_words.extend(SEED_PART4)
    all_words.extend(SEED_PART5)
    all_words.extend(SEED_PART6)
    all_words.extend(SEED_PART7)
    all_words.extend(SEED_PART8)
    all_words.extend(SEED_PART9)
    all_words.extend(SEED_PART10)
    all_words.extend(SEED_PART12)
    
    # Deduplicate
    seen = set()
    unique = []
    for w in all_words:
        key = (w["estonian"], w["finnish"])
        if key not in seen:
            seen.add(key)
            unique.append(w)
    
    # Insert in batches
    batch_size = 100
    async with async_session() as db:
        for i in range(0, len(unique), batch_size):
            batch = unique[i:i+batch_size]
            for w in batch:
                db.add(to_wordpair(w))
            await db.flush()
        await db.commit()
    
    print(f"✅ Seeded {len(unique)} unique word pairs!")

if __name__ == "__main__":
    asyncio.run(seed_quick())
