"""Built-in DCS theater and airport definitions."""

DEFAULT_THEATERS = {
    "Caucasus": {
        "airports": {
            "URKA": {"name": "Anapa", "lat": 45.00480, "lon": 37.34802, "elev": 141, "proxy": "URKA", "runways": ["04", "22"]},
            "URMO": {"name": "Beslan", "lat": 43.20565, "lon": 44.60565, "elev": 1722, "proxy": "URMO", "runways": ["10", "28"]},
            "URKG": {"name": "Gelendzhik", "lat": 44.57288, "lon": 38.01158, "elev": 72, "proxy": "URKG", "runways": ["01", "19"]},
            "URKL": {"name": "Krasnodar-Center", "lat": 45.08700, "lon": 38.93983, "elev": 98, "proxy": "URKK", "runways": ["09", "27"]},
            "URKK": {"name": "Krasnodar-Pashkovsky", "lat": 45.03786, "lon": 39.18814, "elev": 112, "proxy": "URKK", "runways": ["05", "23"]},
            "URKW": {"name": "Krymsk", "lat": 44.96780, "lon": 37.99519, "elev": 66, "proxy": "URKA", "runways": ["04", "22"]},
            "URKH": {"name": "Maykop", "lat": 44.68135, "lon": 40.03503, "elev": 591, "proxy": "URKK", "runways": ["04", "22"]},
            "URMM": {"name": "Mineralnye Vody", "lat": 44.22796, "lon": 43.08135, "elev": 1050, "proxy": "URMM", "runways": ["12", "30"]},
            "XRMF": {"name": "Mozdok", "lat": 43.79181, "lon": 44.60593, "elev": 507, "proxy": "URMM", "runways": ["08", "26"]},
            "URMN": {"name": "Nalchik", "lat": 43.51412, "lon": 43.63644, "elev": 1411, "proxy": "URMN", "runways": ["06", "24"]},
            "URKN": {"name": "Novorossiysk", "lat": 44.66808, "lon": 37.77825, "elev": 131, "proxy": "URKG", "runways": ["04", "22"]},
            "URSS": {"name": "Sochi-Adler", "lat": 43.44435, "lon": 39.94096, "elev": 98, "proxy": "URSS", "runways": ["06", "24"]},
            "UGSB": {"name": "Batumi", "lat": 41.60960, "lon": 41.60000, "elev": 33, "proxy": "UGSB", "runways": ["13", "31"]},
            "UG5X": {"name": "Kobuleti", "lat": 41.92994, "lon": 41.86328, "elev": 59, "proxy": "UGSB", "runways": ["07", "25"]},
            "UGKO": {"name": "Kutaisi", "lat": 42.17768, "lon": 42.48135, "elev": 148, "proxy": "UGKO", "runways": ["07", "25"]},
            "UGKS": {"name": "Senaki-Kolkhi", "lat": 42.24096, "lon": 42.04802, "elev": 43, "proxy": "UGKO", "runways": ["09", "27"]},
            "UG24": {"name": "Soganlug", "lat": 41.64971, "lon": 44.93842, "elev": 1500, "proxy": "UGTB", "runways": ["14", "32"]},
            "UGTB": {"name": "Tbilisi-Lochini", "lat": 41.66695, "lon": 44.95622, "elev": 1574, "proxy": "UGTB", "runways": ["13", "31"]},
            "UG27": {"name": "Vaziani", "lat": 41.62909, "lon": 45.02740, "elev": 1524, "proxy": "UGTB", "runways": ["13", "31"]},
            "UG23": {"name": "Gudauta", "lat": 43.11441, "lon": 40.56977, "elev": 69, "proxy": "URSS", "runways": ["15", "33"]},
            "UGSS": {"name": "Sukhumi", "lat": 42.86102, "lon": 41.12486, "elev": 43, "proxy": "URSS", "runways": ["12", "30"]}
        },
        "runway_mappings": {
            "URSS": {"02": "06", "20": "24"}
        }
    },
    "Syria": {
        "airports": {
            "LTFG": {"name": "Gazipasa Airport", "lat": 36.29888, "lon": 32.30000, "elev": 92, "proxy": "LTFG", "runways": ["08", "26"]},
            "LTAG": {"name": "Incirlik AB", "lat": 37.00190, "lon": 35.42580, "elev": 156, "proxy": "LTAG", "runways": ["05", "23"]},
            "LTAF": {"name": "Adana Sakirpasa Intl", "lat": 36.98194, "lon": 35.28028, "elev": 55, "proxy": "LTAF", "runways": ["05", "23"]},
            "LTAJ": {"name": "Gaziantep Intl", "lat": 36.94778, "lon": 37.47889, "elev": 2305, "proxy": "LTAJ", "runways": ["10", "28"]},
            "LTDA": {"name": "Hatay Airport", "lat": 36.36280, "lon": 36.28220, "elev": 253, "proxy": "LTDA", "runways": ["04", "22"]},
            "LTCS": {"name": "Sanliurfa Airport", "lat": 37.45000, "lon": 38.90000, "elev": 2700, "proxy": "LTCS", "runways": ["04", "22"]},
            "OS71": {"name": "Minakh Helipt", "lat": 36.52194, "lon": 37.04111, "elev": 1614, "proxy": "OSAP", "runways": ["10", "28", "04", "22"]},
            "OSAP": {"name": "Aleppo Intl", "lat": 36.18060, "lon": 37.22440, "elev": 1253, "proxy": "OSAP", "runways": ["09", "27"]},
            "OS66": {"name": "Kuweires AB", "lat": 36.18694, "lon": 37.58306, "elev": 1201, "proxy": "OSAP", "runways": ["10", "28"]},
            "OS62": {"name": "Jirah AB", "lat": 36.09750, "lon": 37.93889, "elev": 1170, "proxy": "OSAP", "runways": ["10", "28"]},
            "AG3611": {"name": "Taftanaz Helipt", "lat": 35.97222, "lon": 36.78306, "elev": 1020, "proxy": "OSAP", "runways": ["10", "28"]},
            "OS57": {"name": "Abu Al-Duhur AB", "lat": 35.73278, "lon": 37.10167, "elev": 820, "proxy": "OSAP", "runways": ["09", "27"]},
            "OS59": {"name": "Tabqa AB", "lat": 35.75444, "lon": 38.56667, "elev": 1083, "proxy": "OSAP", "runways": ["09", "27"]},
            "OSDZ": {"name": "Deir Ez-Zor Airport", "lat": 35.28528, "lon": 40.17583, "elev": 700, "proxy": "OSDZ", "runways": ["10", "28"]},
            "OSLK": {"name": "Bassel Al-Assad", "lat": 35.40080, "lon": 35.94860, "elev": 93, "proxy": "OSLK", "runways": ["17L", "35R", "17R", "35L"]},
            "OS58": {"name": "Hama AB", "lat": 35.11806, "lon": 36.71111, "elev": 983, "proxy": "OSLK", "runways": ["10", "28"]},
            "OS70": {"name": "Al Qusayr AB", "lat": 34.57083, "lon": 36.57194, "elev": 1729, "proxy": "OSLK", "runways": ["10", "28"]},
            "OS65": {"name": "Shayrat AB", "lat": 34.49444, "lon": 36.91111, "elev": 2637, "proxy": "OSDI", "runways": ["11", "29"]},
            "OS72": {"name": "Tiyas AB", "lat": 34.52250, "lon": 37.62889, "elev": 1800, "proxy": "OSDI", "runways": ["09", "27"]},
            "OSPR": {"name": "Palymyra Airport", "lat": 34.55722, "lon": 38.31667, "elev": 1267, "proxy": "OSDI", "runways": ["08", "26"]},
            "OS64": {"name": "An Nasiriyah AB", "lat": 33.91889, "lon": 36.86639, "elev": 2746, "proxy": "OSDI", "runways": ["04", "22"]},
            "OS61": {"name": "Al-Dumayr AB", "lat": 33.61500, "lon": 36.75556, "elev": 2066, "proxy": "OSDI", "runways": ["06", "24"]},
            "OS68": {"name": "Sayqal AB", "lat": 33.67444, "lon": 37.20194, "elev": 2300, "proxy": "OSDI", "runways": ["05", "23", "08", "26"]},
            "OS67": {"name": "Mezzeh AB", "lat": 33.47750, "lon": 36.22333, "elev": 2355, "proxy": "OSDI", "runways": ["06", "24"]},
            "AG4485": {"name": "Marj As Sultan Nth", "lat": 33.50028, "lon": 36.46694, "elev": 2007, "proxy": "OSDI", "runways": ["08", "26"]},
            "AG4486": {"name": "Marj As Sultan Sth", "lat": 33.48694, "lon": 36.47528, "elev": 2007, "proxy": "OSDI", "runways": ["09", "27"]},
            "AG4487": {"name": "Qabr As Sitt Helipt", "lat": 33.45861, "lon": 36.35750, "elev": 2134, "proxy": "OSDI", "runways": ["05", "24"]},
            "OSDI": {"name": "Damascus Intl", "lat": 33.41510, "lon": 36.51440, "elev": 2007, "proxy": "OSDI", "runways": ["05L", "23R", "05R", "23L"]},
            "OLBA": {"name": "Beirut-Rafic Hariri", "lat": 33.82090, "lon": 35.48840, "elev": 87, "proxy": "OLBA", "runways": ["03", "16", "21", "34"]},
            "LCRA": {"name": "RAF Akrotiri", "lat": 34.59060, "lon": 32.98780, "elev": 75, "proxy": "LCRA", "runways": ["10", "28"]},
            "LCLK": {"name": "Larnaca Intl", "lat": 34.87510, "lon": 33.62490, "elev": 8, "proxy": "LCLK", "runways": ["04", "22"]},
            "LLHA": {"name": "Haifa", "lat": 32.80940, "lon": 35.04310, "elev": 28, "proxy": "LLHA", "runways": ["16", "34"]},
            "LLRD": {"name": "Ramat David", "lat": 32.66440, "lon": 35.17940, "elev": 246, "proxy": "LLHA", "runways": ["09", "11", "15", "27", "29", "33"]},
            "OJAI": {"name": "Amman Queen Alia", "lat": 31.72260, "lon": 35.99320, "elev": 2395, "proxy": "OJAI", "runways": ["08", "26"]},
            "OJAM": {"name": "King Hussein Air Base", "lat": 32.35640, "lon": 36.25890, "elev": 2240, "proxy": "OJAI", "runways": ["13", "31"]}
        },
        "runway_mappings": {}
    },
    "Persian Gulf": {
        "airports": {
            "OOKB": {"name": "Khasab", "lat": 26.17972, "lon": 56.24306, "elev": 74, "proxy": "OOKB", "runways": ["01", "19"]},
            "OMRK": {"name": "Ras Al Khaimah", "lat": 25.60222, "lon": 55.94167, "elev": 72, "proxy": "OMRK", "runways": ["16", "34"]},
            "OMSJ": {"name": "Sharjah Intl", "lat": 25.32278, "lon": 55.53111, "elev": 98, "proxy": "OMSJ", "runways": ["12L", "30R", "12R", "30L"]},
            "OMSN": {"name": "Sir Abu Nuayr", "lat": 25.21611, "lon": 54.23667, "elev": 26, "proxy": "OMDB", "runways": ["10", "28"]},
            "OMDB": {"name": "Dubai Intl", "lat": 25.24806, "lon": 55.37917, "elev": 16, "proxy": "OMDB", "runways": ["12L", "30R", "12R", "30L"]},
            "OMFJ": {"name": "Fujairah Intl", "lat": 25.10556, "lon": 56.34028, "elev": 102, "proxy": "OMFJ", "runways": ["11", "29"]},
            "OMDM": {"name": "Al Minhad AB", "lat": 25.02667, "lon": 55.38361, "elev": 172, "proxy": "OMDW", "runways": ["09", "27"]},
            "OMDW": {"name": "Al Maktoum Intl", "lat": 24.88861, "lon": 55.17472, "elev": 123, "proxy": "OMDW", "runways": ["12", "30"]},
            "OMNK": {"name": "Sas Al Nakheel Airport", "lat": 24.44806, "lon": 54.51444, "elev": 10, "proxy": "OMAA", "runways": ["16", "34"]},
            "OMAD": {"name": "Al-Bateen Exec Airport", "lat": 24.43389, "lon": 54.45056, "elev": 13, "proxy": "OMAD", "runways": ["13", "31"]},
            "OMAA": {"name": "Abu Dhabi Intl Airport", "lat": 24.46472, "lon": 54.63917, "elev": 92, "proxy": "OMAA", "runways": ["13L", "31R", "13R", "31L"]},
            "OMAL": {"name": "Al Ain Intl Airport", "lat": 24.27667, "lon": 55.61167, "elev": 814, "proxy": "OMAL", "runways": ["01", "19"]},
            "OMAM": {"name": "Al Dhafra AB", "lat": 24.25778, "lon": 54.53417, "elev": 52, "proxy": "OMAA", "runways": ["13L", "31R", "13R", "31L"]},
            "OMLW": {"name": "Liwa Airbase", "lat": 23.66056, "lon": 53.81222, "elev": 400, "proxy": "OMAA", "runways": ["13", "31"]},
            "OISS": {"name": "Shiraz Intl Airport", "lat": 29.53306, "lon": 52.60972, "elev": 4879, "proxy": "OISS", "runways": ["11L", "29R", "11R", "29L"]},
            "OIKK": {"name": "Kerman Airport", "lat": 30.25750, "lon": 56.95806, "elev": 5746, "proxy": "OIKK", "runways": ["16", "34"]},
            "OIKJ": {"name": "Jiroft Airport", "lat": 28.73139, "lon": 57.66389, "elev": 2664, "proxy": "OIKJ", "runways": ["13", "31"]},
            "OISL": {"name": "Lar Airbase", "lat": 27.67472, "lon": 54.36806, "elev": 2636, "proxy": "OISL", "runways": ["09", "27"]},
            "OIKP": {"name": "Havadarya", "lat": 27.15972, "lon": 56.18306, "elev": 51, "proxy": "OIKB", "runways": ["08", "26"]},
            "OIKB": {"name": "Bandar Abbas Intl", "lat": 27.20361, "lon": 56.37028, "elev": 17, "proxy": "OIKB", "runways": ["03L", "21R", "03R", "21L"]},
            "OIBV": {"name": "Lavan Island Airport", "lat": 26.81528, "lon": 53.34139, "elev": 75, "proxy": "OIBV", "runways": ["11", "29"]},
            "OIBK": {"name": "Kish Intl Airport", "lat": 26.52944, "lon": 53.96472, "elev": 115, "proxy": "OIBK", "runways": ["09L", "27R", "09R", "27L"]},
            "OIBL": {"name": "Bandar Lengeh", "lat": 26.53056, "lon": 54.81306, "elev": 76, "proxy": "OIBL", "runways": ["08", "26"]},
            "OIKQ": {"name": "Qeshm Island", "lat": 26.76611, "lon": 55.91806, "elev": 17, "proxy": "OIKQ", "runways": ["05", "23"]},
            "OITK": {"name": "Tunb Kochak", "lat": 26.24333, "lon": 55.14917, "elev": 16, "proxy": "OIKB", "runways": ["08", "26"]},
            "OIGI": {"name": "Tunb Island AFB", "lat": 26.25139, "lon": 55.31111, "elev": 43, "proxy": "OIKB", "runways": ["03", "21"]},
            "OIBS": {"name": "Sirri Island", "lat": 25.90333, "lon": 54.54806, "elev": 16, "proxy": "OIBK", "runways": ["12", "30"]},
            "OIBA": {"name": "Abu Musa Island Airport", "lat": 25.87500, "lon": 55.02111, "elev": 16, "proxy": "OIBA", "runways": ["08", "26"]},
            "OISJ": {"name": "Bandar-e-Jask Airfield", "lat": 25.65028, "lon": 57.79194, "elev": 26, "proxy": "OISJ", "runways": ["06", "24"]}
        },
        "runway_mappings": {}
    },
    "Nevada": {
        "airports": {},
        "runway_mappings": {}
    },
    "Sinai": {
        "airports": {},
        "runway_mappings": {}
    },
    "Marianas": {
        "airports": {
            "PG01": {"name": "Orote Field", "lat": 13.43778, "lon": 144.64167, "elev": 93, "proxy": "PGUM", "runways": ["07", "25"]},
            "PGUM": {"name": "Antonio B. Won Pat Intl", "lat": 13.48333, "lon": 144.79583, "elev": 255, "proxy": "PGUM", "runways": ["06L", "24R", "06R", "24L"]},
            "PGUA": {"name": "Andersen AFB", "lat": 13.58389, "lon": 144.92972, "elev": 551, "proxy": "PGUA", "runways": ["06L", "24R", "06R", "24L"]},
            "PG02": {"name": "North-West Field", "lat": 13.62194, "lon": 144.85889, "elev": 523, "proxy": "PGUA", "runways": ["06", "24"]},
            "PGRO": {"name": "Rota Intl", "lat": 14.17417, "lon": 145.24278, "elev": 607, "proxy": "PGRO", "runways": ["09", "27"]},
            "PGWT": {"name": "Tinian Intl", "lat": 14.99917, "lon": 145.61889, "elev": 268, "proxy": "PGWT", "runways": ["08", "26"]},
            "PG03": {"name": "Tinian North Field", "lat": 15.07444, "lon": 145.63833, "elev": 125, "proxy": "PGWT", "runways": ["09", "27"]},
            "PGSN": {"name": "Saipan Intl", "lat": 15.11889, "lon": 145.72889, "elev": 213, "proxy": "PGSN", "runways": ["07", "25", "06", "24"]}
        },
        "runway_mappings": {}
    },
    "Kola": {
        "airports": {},
        "runway_mappings": {}
    },
    "South Atlantic": {
        "airports": {},
        "runway_mappings": {}
    }
}

THEATER_CENTERS = {
    "Caucasus": (43.0, 42.0, 7),
    "Syria": (34.8, 36.5, 7),
    "Persian Gulf": (26.5, 55.0, 7),
    "Nevada": (36.8, -115.5, 7),
    "Sinai": (30.0, 33.5, 7),
    "Marianas": (14.2, 145.0, 8),
    "Kola": (67.8, 30.0, 6),
    "South Atlantic": (-52.0, -62.0, 6),
}
