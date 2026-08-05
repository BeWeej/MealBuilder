# init_db.py
import sqlite3

con = sqlite3.connect("voeding.db")
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS voedingsmiddelen")

cur.execute("""
CREATE TABLE voedingsmiddelen (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    naam     TEXT NOT NULL UNIQUE,
    groep    TEXT NOT NULL,
    gewicht  REAL NOT NULL,   -- gram dat overeenkomt met 100 kcal
    eiwit    REAL NOT NULL,   -- g per 100 g product
    kh       REAL NOT NULL,
    vet      REAL NOT NULL
)
""")

# naam, groep, gewicht(100kcal), eiwit, kh, vet
rijen = [
    ("Gepofte aardappel",              "Koolhydraten",           110, 2.0, 20.0, 0.2),
    ("Averbode brood (1 dikke snede)", "Koolhydraten",            40, 9.0, 45.0, 3.0),
    ("Bruine rijst (droog)",           "Koolhydraten",            28, 7.5, 72.0, 2.7),
    ("Volkoren pasta (droog)",         "Koolhydraten",            29, 13.0, 64.0, 2.5),

    ("Lupinebonen (gekookt)",          "Eiwitten/koolhydraten",   83, 16.0, 10.0, 2.9),
    ("Edamame (gekookt)",              "Eiwitten/koolhydraten",   82, 11.0, 9.0, 5.0),
    ("Noten - amandel/pecan/hazel",    "Eiwitten/koolhydraten",   16, 15.0, 12.0, 55.0),
    ("Noten - macadamia",              "Eiwitten/koolhydraten",   14, 8.0, 14.0, 76.0),

    ("Tonijn/kip/mager vlees (rauw)",  "Eiwitten",                85, 22.0, 0.0, 2.0),
    ("Volle yoghurt",                  "Eiwitten",               170, 3.5, 4.5, 3.5),

    ("Zalmfilet",                      "Vetten",                  48, 20.0, 0.0, 13.0),
    ("Cottage cheese",                 "Vetten",                 100, 11.0, 3.5, 4.3),
    ("Feta",                           "Vetten",                  38, 14.0, 1.0, 21.0),
    ("Mozzarella",                     "Vetten",                  35, 18.0, 2.5, 22.0),
    ("Oude kaas",                      "Vetten",                  25, 25.0, 0.0, 35.0),
    ("Avocado",                        "Vetten",                  63, 2.0, 1.0, 15.0),
    ("Olijfolie (1 kleine eetlepel)",  "Vetten",                  11, 0.0, 0.0, 100.0),
    ("Eieren (1 groot ei)",            "Vetten",                  70, 13.0, 0.5, 11.0),

    ("Champignons",                    "Groenten",               455, 3.0, 1.0, 0.3),
    ("Broccoli",                       "Groenten",               294, 3.0, 4.0, 0.4),
    ("Spruiten",                       "Groenten",               233, 3.4, 5.0, 0.3),
    ("Bloemkool",                      "Groenten",               400, 2.0, 3.0, 0.3),
    ("Courgette",                      "Groenten",               588, 1.2, 2.0, 0.3),
    ("Witloof",                        "Groenten",               588, 1.0, 2.0, 0.2),
    ("Boerenkool",                     "Groenten",               204, 4.3, 4.0, 1.5),
    ("Pastinaak",                      "Groenten",               133, 1.2, 16.0, 0.3),
    ("Zoete aardappel",                "Groenten",               117, 1.6, 20.0, 0.1),
    ("Erwten",                         "Groenten",               123, 5.4, 11.0, 0.4),
    ("Mais",                           "Groenten",               104, 3.3, 19.0, 1.4),
]

cur.executemany(
    "INSERT INTO voedingsmiddelen (naam, groep, gewicht, eiwit, kh, vet) VALUES (?, ?, ?, ?, ?, ?)",
    rijen,
)

con.commit()
con.close()
print(f"Klaar. {len(rijen)} items met groep + macro's in voeding.db")