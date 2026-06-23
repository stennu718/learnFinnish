"""Seed data — 50 core Estonian-Finnish word pairs (cognates first)."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WordPair

SEED_WORDS = [
    # Cognates (nearly identical)
    {"estonian": "jää", "finnish": "jää", "estonian_example": "Jääl on hästi külm.", "finnish_example": "Jäällä on hyvin kylmä.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "vesi", "finnish": "vesi", "estonian_example": "Vesi on selge.", "finnish_example": "Vesi on kirkas.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "tuli", "finnish": "tuli", "estonian_example": "Tuli on soe.", "finnish_example": "Tuli on lämmin.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "maa", "finnish": "maa", "estonian_example": "Maa on suur.", "finnish_example": "Maa on suuri.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "päev", "finnish": "päivä", "estonian_example": "Täna on ilus päev.", "finnish_example": "Tänään on kaunis päivä.", "category": "time", "is_cognate": True, "difficulty": 1},
    {"estonian": "öö", "finnish": "yö", "estonian_example": "Öö on pime.", "finnish_example": "Yö on pimeä.", "category": "time", "is_cognate": True, "difficulty": 1},
    {"estonian": "käsi", "finnish": "käsi", "estonian_example": "Mu käsi on soe.", "finnish_example": "Kädeni on lämmin.", "category": "body", "is_cognate": True, "difficulty": 1},
    {"estonian": "suu", "finnish": "suu", "estonian_example": "Suuk on suur.", "finnish_example": "Suu on suuri.", "category": "body", "is_cognate": True, "difficulty": 1},
    {"estonian": "silm", "finnish": "silmä", "estonian_example": "Mu silm on sinine.", "finnish_example": "Silmäni on sininen.", "category": "body", "is_cognate": True, "difficulty": 1},
    {"estonian": "nina", "finnish": "nenä", "estonian_example": "Mu nina on punane.", "finnish_example": "Nenäni on punainen.", "category": "body", "is_cognate": True, "difficulty": 1},
    {"estonian": "juuksed", "finnish": "hiukset", "estonian_example": "Tal on pikad juuksed.", "finnish_example": "Hänellä on pitkät hiukset.", "category": "body", "is_cognate": True, "difficulty": 2},
    {"estonian": "sõber", "finnish": "ystävä", "estonian_example": "See on mu sõber.", "finnish_example": "Tämä on ystäväni.", "category": "people", "is_cognate": False, "difficulty": 2},
    {"estonian": "kool", "finnish": "koulu", "estonian_example": "Ma lähen kooli.", "finnish_example": "Menen kouluun.", "category": "education", "is_cognate": True, "difficulty": 1},
    {"estonian": "raamat", "finnish": "kirja", "estonian_example": "Ma loen raamatut.", "finnish_example": "Luen kirjaa.", "category": "education", "is_cognate": False, "difficulty": 2},
    {"estonian": "tuba", "finnish": "tupa", "estonian_example": "Tuba on suur.", "finnish_example": "Tupa on suuri.", "category": "home", "is_cognate": True, "difficulty": 1},
    {"estonian": "aken", "finnish": "ikkuna", "estonian_example": "Aken on avatud.", "finnish_example": "Ikkuna on auki.", "category": "home", "is_cognate": False, "difficulty": 2},
    {"estonian": "uks", "finnish": "ovi", "estonian_example": "Uks on suletud.", "finnish_example": "Ovi on kiinni.", "category": "home", "is_cognate": False, "difficulty": 2},
    {"estonian": "tool", "finnish": "tuoli", "estonian_example": "Tool on mugav.", "finnish_example": "Tuoli on mukava.", "category": "home", "is_cognate": True, "difficulty": 1},
    {"estonian": "laud", "finnish": "pöytä", "estonian_example": "Laud on pikk.", "finnish_example": "Pöytä on pieni.", "category": "home", "is_cognate": False, "difficulty": 2},
    {"estonian": "voodi", "finnish": "vuode", "estonian_example": "Voodi on pehme.", "finnish_example": "Vuode on pehmeä.", "category": "home", "is_cognate": True, "difficulty": 1},
    # More cognates
    {"estonian": "linn", "finnish": "linna", "estonian_example": "Linn on vana.", "finnish_example": "Linna on vanha.", "category": "places", "is_cognate": True, "difficulty": 1},
    {"estonian": "järv", "finnish": "järvi", "estonian_example": "Järv on suur.", "finnish_example": "Järvi on suuri.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "meri", "finnish": "meri", "estonian_example": "Meri on sinine.", "finnish_example": "Meri on sininen.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "mets", "finnish": "metsä", "estonian_example": "Mets on tihe.", "finnish_example": "Metsä on tiheä.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "lind", "finnish": "lintu", "estonian_example": "Lind lendab.", "finnish_example": "Lintu lentää.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "kala", "finnish": "kala", "estonian_example": "Kala ujub.", "finnish_example": "Kala ui.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "koer", "finnish": "koira", "estonian_example": "Koer haugub.", "finnish_example": "Koira haukkuu.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "kass", "finnish": "kissa", "estonian_example": "Kass norskab.", "finnish_example": "Kissa nukkuu.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "puu", "finnish": "puu", "estonian_example": "Puu on kõrge.", "finnish_example": "Puu on korkea.", "category": "nature", "is_cognate": True, "difficulty": 1},
    {"estonian": "lill", "finnish": "kukka", "estonian_example": "Lill on ilus.", "finnish_example": "Kukka on kaunis.", "category": "nature", "is_cognate": False, "difficulty": 2},
    # Food
    {"estonian": "leib", "finnish": "leipä", "estonian_example": "Leib on värske.", "finnish_example": "Leipä on tuore.", "category": "food", "is_cognate": True, "difficulty": 1},
    {"estonian": "piim", "finnish": "maito", "estonian_example": "Piim on külm.", "finnish_example": "Maito on kylmä.", "category": "food", "is_cognate": False, "difficulty": 2},
    {"estonian": "sai", "finnish": "sämpylä", "estonian_example": "Sai on hea.", "finnish_example": "Sämpylä on hyvä.", "category": "food", "is_cognate": False, "difficulty": 2},
    {"estonian": "õlu", "finnish": "olut", "estonian_example": "Õlu on külm.", "finnish_example": "Olut on kylmä.", "category": "food", "is_cognate": True, "difficulty": 1},
    {"estonian": "kohv", "finnish": "kahvi", "estonian_example": "Kohv on tugev.", "finnish_example": "Kahvi on vahva.", "category": "food", "is_cognate": True, "difficulty": 1},
    {"estonian": "tee", "finnish": "tee", "estonian_example": "Tee on soe.", "finnish_example": "Tee on kuuma.", "category": "food", "is_cognate": True, "difficulty": 1},
    {"estonian": "suhkur", "finnish": "sokeri", "estonian_example": "Suhkur on magus.", "finnish_example": "Sokeri on makea.", "category": "food", "is_cognate": False, "difficulty": 2},
    {"estonian": "sool", "finnish": "suola", "estonian_example": "Sool on soolane.", "finnish_example": "Suola on suolainen.", "category": "food", "is_cognate": True, "difficulty": 1},
    {"estonian": "liha", "finnish": "liha", "estonian_example": "Liha on maitsev.", "finnish_example": "Liha on makoinen.", "category": "food", "is_cognate": True, "difficulty": 1},
    {"estonian": "kartul", "finnish": "peruna", "estonian_example": "Kartul on küps.", "finnish_example": "Peruna on kypsä.", "category": "food", "is_cognate": False, "difficulty": 2},
    # Numbers
    {"estonian": "üks", "finnish": "yksi", "estonian_example": "Üks pliiats.", "finnish_example": "Yksi kynä.", "category": "numbers", "is_cognate": True, "difficulty": 1},
    {"estonian": "kaks", "finnish": "kaksi", "estonian_example": "Kaks inimest.", "finnish_example": "Kaksi ihmistä.", "category": "numbers", "is_cognate": True, "difficulty": 1},
    {"estonian": "kolm", "finnish": "kolme", "estonian_example": "Kolm õuna.", "finnish_example": "Kolme omenaa.", "category": "numbers", "is_cognate": True, "difficulty": 1},
    {"estonian": "neli", "finnish": "neljä", "estonian_example": "Neli aastaaega.", "finnish_example": "Neljä vuodenaikaa.", "category": "numbers", "is_cognate": True, "difficulty": 1},
    {"estonian": "viis", "finnish": "viisi", "estonian_example": "Viis sõrme.", "finnish_example": "Viisi sormea.", "category": "numbers", "is_cognate": True, "difficulty": 1},
    # Common words
    {"estonian": "head aega", "finnish": "hyvää matkaa", "estonian_example": "Head aega!", "finnish_example": "Hyvää matkaa!", "category": "phrases", "is_cognate": False, "difficulty": 1},
    {"estonian": "tänan", "finnish": "kiitos", "estonian_example": "Tänan sind.", "finnish_example": "Kiitos sinua.", "category": "phrases", "is_cognate": False, "difficulty": 1},
    {"estonian": "palun", "finnish": "ole hyvä", "estonian_example": "Palun aidake.", "finnish_example": "Ole hyvä, auta.", "category": "phrases", "is_cognate": False, "difficulty": 1},
    {"estonian": "tere", "finnish": "hei", "estonian_example": "Tere hommikust!", "finnish_example": "Huomenta!", "category": "phrases", "is_cognate": False, "difficulty": 1},
    {"estonian": "jah", "finnish": "kyllä", "estonian_example": "Jah, muidugi.", "finnish_example": "Kyllä, tietysti.", "category": "phrases", "is_cognate": False, "difficulty": 1},
    {"estonian": "ei", "finnish": "ei", "estonian_example": "Ei, aitäh.", "finnish_example": "Ei, kiitos.", "category": "phrases", "is_cognate": True, "difficulty": 1},
]


async def seed_database(db: AsyncSession):
    """Insert seed word pairs if table is empty."""
    from sqlalchemy import select, func
    result = await db.execute(select(func.count(WordPair.id)))
    count = result.scalar()
    if count > 0:
        return  # Already seeded

    for word in SEED_WORDS:
        pair = WordPair(**word)
        db.add(pair)

    await db.flush()
