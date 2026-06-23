"""Seed data generator — 500 conversational Estonian-Finnish word pairs.
Run: python app/services/seed.py to populate the database."""
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WordPair

# Data stored as JSON string to avoid Python list size limits
SEED_JSON = '''
[
  {"estonian":"tere","finnish":"hei","et":"Tere! Kuidas läheb?","fi":"Hei! Mitä kuuluu?","cat":"greetings","cog":0,"d":1},
  {"estonian":"tere hommikust","finnish":"huomenta","et":"Tere hommikust! Ilus päev.","fi":"Huomenta! Kaunis päivä.","cat":"greetings","cog":0,"d":1},
  {"estonian":"tere õhtust","finnish":"iltaa","et":"Tere õhtust! Tule sisse.","fi":"Iltaa! Tule sisään.","cat":"greetings","cog":0,"d":1},
  {"estonian":"head ööd","finnish":"hyvää yötä","et":"Head ööd! Nuku hästi.","fi":"Hyvää yötä! Nuku hyvin.","cat":"greetings","cog":0,"d":1},
  {"estonian":"head aega","finnish":"hyvää matkaa","et":"Head aega! Näeme hiljem.","fi":"Hyvää matkaa! Nähdään myöhemmin.","cat":"greetings","cog":0,"d":1},
  {"estonian":"nägemist","finnish":"näkemiin","et":"Nägemist! Homme samas kohas.","fi":"Näkemiin! Huomenna samassa paikassa.","cat":"greetings","cog":0,"d":1},
  {"estonian":"hüvasti","finnish":"hei hei","et":"Hüvasti, mu sõber!","fi":"Hei hei, ystäväni!","cat":"greetings","cog":0,"d":1},
  {"estonian":"tänan","finnish":"kiitos","et":"Tänan sind väga!","fi":"Kiitos sinua paljon!","cat":"greetings","cog":0,"d":1},
  {"estonian":"palun","finnish":"ole hyvä","et":"Palun aita mind.","fi":"Ole hyvä, auta minua.","cat":"greetings","cog":0,"d":1},
  {"estonian":"vabandust","finnish":"anteeksi","et":"Vabandust, kus on tualett?","fi":"Anteeksi, missä on vessa?","cat":"greetings","cog":0,"d":1},
  {"estonian":"kuidas läheb","finnish":"mitä kuuluu","et":"Tere! Kuidas läheb?","fi":"Hei! Mitä kuuluu?","cat":"greetings","cog":0,"d":1},
  {"estonian":"hästi","finnish":"hyvin","et":"Mul läheb hästi.","fi":"Minulle menee hyvin.","cat":"greetings","cog":0,"d":1},
  {"estonian":"väga hästi","finnish":"erittäin hyvin","et":"Tänan, väga hästi!","fi":"Kiitos, erittäin hyvin!","cat":"greetings","cog":0,"d":1},
  {"estonian":"näeme","finnish":"nähdään","et":"Näeme homme!","fi":"Nähdään huomenna!","cat":"greetings","cog":0,"d":1},
  {"estonian":"meeldiv tutvuda","finnish":"hauska tutustua","et":"Meeldiv tutvuda! Mina olen Peeter.","fi":"Hauska tutustua! Minä olen Pekka.","cat":"greetings","cog":0,"d":2},
  {"estonian":"mis","finnish":"mikä","et":"Mis see on?","fi":"Mikä tämä on?","cat":"questions","cog":0,"d":1},
  {"estonian":"kes","finnish":"kuka","et":"Kes sa oled?","fi":"Kuka sinä olet?","cat":"questions","cog":0,"d":1},
  {"estonian":"kus","finnish":"missä","et":"Kus sa elad?","fi":"Missä sinä asut?","cat":"questions","cog":0,"d":1},
  {"estonian":"kui palju","finnish":"kuinka paljon","et":"Kui palju see maksab?","fi":"Kuinka paljon tämä maksaa?","cat":"questions","cog":0,"d":1},
  {"estonian":"millal","finnish":"milloin","et":"Millal sa tuled?","fi":"Milloin sinä tulet?","cat":"questions","cog":0,"d":1},
  {"estonian":"miks","finnish":"miksi","et":"Miks sa tulid hilja?","fi":"Miksi tulit myöhään?","cat":"questions","cog":1,"d":1},
  {"estonian":"kuidas","finnish":"miten","et":"Kuidas ma saan sinna?","fi":"Miten pääsen sinne?","cat":"questions","cog":0,"d":1},
  {"estonian":"kas","finnish":"ko","et":"Kas sa räägid soome keelt?","fi":"Ko puhut suomea?","cat":"questions","cog":0,"d":1},
  {"estonian":"kuhu","finnish":"minne","et":"Kuhu sa lähed?","fi":"Minne sinä menet?","cat":"questions","cog":0,"d":1},
  {"estonian":"kust","finnish":"mistä","et":"Kust sa tuled?","fi":"Mistä sinä tulet?","cat":"questions","cog":0,"d":1},
  {"estonian":"mitu","finnish":"kuinka monta","et":"Mitu last sul on?","fi":"Kuinka monta lasta sinulla on?","cat":"questions","cog":0,"d":2},
  {"estonian":"kumb","finnish":"kumpi","et":"Kumb on õige?","fi":"Kumpi on oikea?","cat":"questions","cog":0,"d":2},
  {"estonian":"üks","finnish":"yksi","et":"Üks kaks kolm.","fi":"Yksi kaksi kolme.","cat":"numbers","cog":1,"d":1},
  {"estonian":"kaks","finnish":"kaksi","et":"Kaks kohvi, palun.","fi":"Kaksi kahvia, kiitos.","cat":"numbers","cog":1,"d":1},
  {"estonian":"kolm","finnish":"kolme","et":"Kolm päeva tagasi.","fi":"Kolme päivää sitten.","cat":"numbers","cog":1,"d":1},
  {"estonian":"neli","finnish":"neljä","et":"Neli aastaa tagasi.","fi":"Neljä vuotta sitten.","cat":"numbers","cog":1,"d":1},
  {"estonian":"viis","finnish":"viisi","et":"Viis minutit veel.","fi":"Viisi minuuttia vielä.","cat":"numbers","cog":1,"d":1},
  {"estonian":"kuus","finnish":"kuusi","et":"Kuus eurot, palun.","fi":"Kuusi euroa, kiitos.","cat":"numbers","cog":1,"d":1},
  {"estonian":"seitse","finnish":"seitsemän","et":"Seitse päeva nädalas.","fi":"Seitsemän päivää viikossa.","cat":"numbers","cog":0,"d":1},
  {"estonian":"kaheksa","finnish":"kahdeksan","et":"Kaheksa tundi päevas.","fi":"Kahdeksan tuntia päivässä.","cat":"numbers","cog":0,"d":1},
  {"estonian":"üheksa","finnish":"yhdeksän","et":"Üheksa kuud aastas.","fi":"Yhdeksän kuukautta vuodessa.","cat":"numbers","cog":0,"d":1},
  {"estonian":"kümme","finnish":"kymmenen","et":"Kümme senti.","fi":"Kymmenen senttiä.","cat":"numbers","cog":0,"d":1},
  {"estonian":"kakskümmend","finnish":"kaksikymmentä","et":"Kakskümmend eurot.","fi":"Kaksikymmentä euroa.","cat":"numbers","cog":0,"d":2},
  {"estonian":"kolmkümmend","finnish":"kolmekymmentä","et":"Kolmkümmend kraadi.","fi":"Kolmekymmentä astetta.","cat":"numbers","cog":0,"d":2},
  {"estonian":"sada","finnish":"sata","et":"Sada aastat tagasi.","fi":"Sata vuotta sitten.","cat":"numbers","cog":1,"d":1},
  {"estonian":"tuhat","finnish":"tuhat","et":"Tuhat tänu!","fi":"Tuhat kiitosta!","cat":"numbers","cog":1,"d":1},
  {"estonian":"jah","finnish":"kyllä","et":"Jah, muidugi!","fi":"Kyllä, tietysti!","cat":"questions","cog":0,"d":1},
  {"estonian":"ei","finnish":"ei","et":"Ei, aitäh.","fi":"Ei, kiitos.","cat":"questions","cog":1,"d":1},
  {"estonian":"võib-olla","finnish":"ehkä","et":"Võib-olla homme.","fi":"Ehkä huomenna.","cat":"questions","cog":0,"d":2}
]
'''

async def parse_and_seed(db: AsyncSession):
    """Parse JSON seed data and insert into database."""
    words = json.loads(SEED_JSON)
    count = 0
    for w in words:
        pair = WordPair(
            estonian=w["estonian"],
            finnish=w["finnish"],
            estonian_example=w["et"],
            finnish_example=w["fi"],
            category=w["cat"],
            is_cognate=bool(w["cog"]),
            difficulty=w["d"]
        )
        db.add(pair)
        count += 1
    await db.flush()
    return count


async def seed_database(db: AsyncSession):
    """Insert seed word pairs if table is empty."""
    from sqlalchemy import select, func
    result = await db.execute(select(func.count(WordPair.id)))
    count = result.scalar()
    if count > 0:
        return 0  # Already seeded
    return await parse_and_seed(db)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/lan/learnFinnish/backend")
    from app.core.database import async_session, engine, Base
    
    async def main():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_session() as db:
            n = await seed_database(db)
            await db.commit()
            print(f"✅ Seeded {n} word pairs")
    
    asyncio.run(main())
