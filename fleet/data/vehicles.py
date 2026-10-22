"""Forty demo rental cars.

Prices are stored in US dollars. The Ukrainian interface multiplies by
UAH_PER_USD (41.50), so an integer dollar price is shown as an exact
hryvnia amount. Figures in the descriptions are typical equipment for
the named trim, not certified specifications.
"""

from decimal import Decimal


def _car(**kwargs):
    kwargs["price"] = Decimal(kwargs["price"])
    return kwargs


# price is USD. Shown in Ukrainian as price * 41.50 UAH.
VEHICLES = (
    _car(
        slug="toyota-yaris",
        brand="Toyota",
        model="Yaris",
        year=2023,
        price="28",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Economy",
        plate="KA 2401 IK",
        color="Silver",
        mileage=18400,
        description=(
            "A compact 2023 Yaris with the 1.5-litre petrol engine and an automatic gearbox. "
            "Light to park, cheap to run, and easy for a city weekend."
        ),
        must=["yaris"],
        reject=["cross", "gr yaris", "verso", "aygo"],
    ),
    _car(
        slug="volkswagen-polo",
        brand="Volkswagen",
        model="Polo",
        year=2021,
        price="24",
        seats=5,
        transmission="Manual",
        fuel="Gasoline",
        car_class="Economy",
        plate="KA 2402 IK",
        color="White",
        mileage=41200,
        description=(
            "A 2021 Polo 1.0 TSI with a manual gearbox. Small outside, practical inside, "
            "and a straightforward economy rental."
        ),
        must=["polo"],
        reject=["polaris", "polo gti", "virtus"],
    ),
    _car(
        slug="hyundai-i20",
        brand="Hyundai",
        model="i20",
        year=2024,
        price="32",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Economy",
        plate="KA 2403 IK",
        color="Blue",
        mileage=9600,
        description=(
            "A nearly new i20 with a small petrol engine and an automatic transmission. "
            "Quiet enough for commuting and simple to place in a tight street."
        ),
        must=["i20"],
        reject=["i20 n", "ioniq", "i30"],
    ),
    _car(
        slug="renault-clio",
        brand="Renault",
        model="Clio",
        year=2020,
        price="26",
        seats=5,
        transmission="Manual",
        fuel="Diesel",
        car_class="Economy",
        plate="KA 2404 IK",
        color="Red",
        mileage=63800,
        description=(
            "A 2020 Clio with the 1.5-litre diesel and a manual gearbox. "
            "A modest economy hatchback for longer highway days."
        ),
        must=["clio"],
        reject=["clio v6", "williams", "grandtour"],
    ),
    _car(
        slug="skoda-fabia",
        brand="Skoda",
        model="Fabia",
        year=2022,
        price="22",
        seats=5,
        transmission="Manual",
        fuel="Gasoline",
        car_class="Economy",
        plate="KA 2405 IK",
        color="Grey",
        mileage=35700,
        description=(
            "A 2022 Fabia 1.0 TSI with a manual gearbox. Honest economy transport "
            "with a useful boot for a car this size."
        ),
        must=["fabia"],
        reject=["fabia rs"],
    ),
    _car(
        slug="peugeot-208",
        brand="Peugeot",
        model="208",
        year=2023,
        price="34",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Economy",
        plate="KA 2406 IK",
        color="Yellow",
        mileage=22100,
        description=(
            "A 2023 Peugeot 208 PureTech petrol with an automatic gearbox. "
            "The small steering wheel and bright cabin make short trips less dull."
        ),
        must=["208"],
        reject=["2008", "e-208", "308", "508", "rcz"],
    ),
    _car(
        slug="volkswagen-golf",
        brand="Volkswagen",
        model="Golf",
        year=2022,
        price="40",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Comfort",
        plate="KA 2407 IK",
        color="Grey",
        mileage=29400,
        description=(
            "A 2022 Golf 2.0 TDI with an automatic gearbox. A compact hatchback "
            "that still feels settled on a motorway."
        ),
        must=["golf"],
        reject=["gti", "r32", "golf r", "cabriolet", "variant", "plus", "sportsvan", "sportwagen"],
    ),
    _car(
        slug="mazda-3",
        brand="Mazda",
        model="3",
        year=2023,
        price="42",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Comfort",
        plate="KA 2408 IK",
        color="Red",
        mileage=16800,
        description=(
            "A 2023 Mazda 3 with the 2.0-litre petrol engine and an automatic gearbox. "
            "Sharper to drive than most compact rentals, with a quiet cabin."
        ),
        must=["mazda 3", "mazda3"],
        reject=["mazda 6", "cx-3", "cx-30", "mx-30", "mps"],
        any_must=True,
    ),
    _car(
        slug="honda-civic",
        brand="Honda",
        model="Civic",
        year=2022,
        price="44",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Comfort",
        plate="KA 2409 IK",
        color="Blue",
        mileage=25300,
        description=(
            "A 2022 Civic hatchback with a turbo petrol engine and an automatic gearbox. "
            "Roomy for the class and calm at speed."
        ),
        must=["civic"],
        reject=["type r", "civic type", "cr-v", "accord"],
    ),
    _car(
        slug="toyota-corolla",
        brand="Toyota",
        model="Corolla",
        year=2024,
        price="46",
        seats=5,
        transmission="Automatic",
        fuel="Hybrid",
        car_class="Comfort",
        plate="KA 2410 IK",
        color="White",
        mileage=11200,
        description=(
            "A 2024 Corolla hybrid with the 1.8-litre petrol-electric setup and an automatic gearbox. "
            "A quiet compact for mixed city and highway use."
        ),
        must=["corolla"],
        reject=["corolla cross", "gr corolla", "verso"],
    ),
    _car(
        slug="seat-leon",
        brand="Seat",
        model="Leon",
        year=2021,
        price="36",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Comfort",
        plate="KA 2411 IK",
        color="Grey",
        mileage=47600,
        description=(
            "A 2021 Leon 1.5 TSI with an automatic gearbox. A compact hatchback "
            "with enough pace for a mountain road and a normal rental bill."
        ),
        must=["leon"],
        reject=["leon cupra", "cupra leon", "altea", "mk1", "mk2"],
    ),
    _car(
        slug="bmw-3-series",
        brand="BMW",
        model="3 Series",
        year=2023,
        price="78",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Premium",
        plate="BB 5678 KK",
        color="Black",
        mileage=14200,
        description=(
            "A 2023 320i, the petrol 3 Series, with an automatic gearbox. "
            "A business sedan that is still engaging on an empty road."
        ),
        must=["3 series", "320", "330i", "320i"],
        reject=["5 series", "7 series", "4 series", "2 series", "8 series", "x3", "x5", "i3", "i4", "m3", "m4"],
        any_must=True,
    ),
    _car(
        slug="mercedes-c-class",
        brand="Mercedes-Benz",
        model="C-Class",
        year=2022,
        price="72",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2413 IK",
        color="Silver",
        mileage=28600,
        description=(
            "A 2022 C 220 d with an automatic gearbox. Diesel torque for highway work "
            "and a cabin aimed at business travel."
        ),
        must=["c-class", "c class", "c 220", "c220", "w206"],
        reject=["e-class", "s-class", "glc", "cla", "glb", "gle", "amg"],
        any_must=True,
    ),
    _car(
        slug="audi-a4",
        brand="Audi",
        model="A4",
        year=2022,
        price="68",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="GG 3344 KK",
        color="Dark Blue",
        mileage=23100,
        description=(
            "A 2022 A4 35 TDI, a 2.0-litre diesel with an automatic gearbox. "
            "Understated business transport with quattro available on this fleet car."
        ),
        must=["a4"],
        reject=["allroad", "rs4", "s4", "a5", "a6", "a3", "q5", "button", "vent"],
    ),
    _car(
        slug="volkswagen-passat",
        brand="Volkswagen",
        model="Passat",
        year=2021,
        price="50",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Comfort",
        plate="EE 7890 KK",
        color="Blue",
        mileage=52400,
        description=(
            "A 2021 Passat 2.0 TDI with an automatic gearbox. A wide, calm sedan "
            "for airport runs and week-long trips."
        ),
        must=["passat"],
        reject=["passat cc", "alltrack"],
    ),
    _car(
        slug="skoda-superb",
        brand="Skoda",
        model="Superb",
        year=2022,
        price="56",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Comfort",
        plate="KA 2416 IK",
        color="Black",
        mileage=33800,
        description=(
            "A 2022 Superb 2.0 TDI with an automatic gearbox. Extra rear legroom "
            "and a large boot without a luxury-badge price."
        ),
        must=["superb"],
        reject=["octavia", "kodiaq"],
    ),
    _car(
        slug="lexus-es",
        brand="Lexus",
        model="ES 300h",
        year=2023,
        price="88",
        seats=5,
        transmission="Automatic",
        fuel="Hybrid",
        car_class="Premium",
        plate="KA 2417 IK",
        color="White",
        mileage=15600,
        description=(
            "A 2023 ES 300h, the 2.5-litre hybrid sedan, with an automatic gearbox. "
            "Soft, quiet, and aimed at a long day in the back seat as much as the front."
        ),
        must=["es 300", "es300", "lexus es"],
        reject=["rx", "nx", "ux", "ls "],
        any_must=True,
    ),
    _car(
        slug="bmw-5-series",
        brand="BMW",
        model="5 Series",
        year=2022,
        price="116",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2418 IK",
        color="Black",
        mileage=27400,
        description=(
            "A 2022 520d with an automatic gearbox. A full-size executive diesel "
            "for clients who want the 5 Series rather than a compact sedan."
        ),
        must=["5 series", "520d", "530d", "520d"],
        reject=["3 series", "7 series", "x5", "4 series", "m5", "i5"],
        any_must=True,
    ),
    _car(
        slug="mercedes-e-class",
        brand="Mercedes-Benz",
        model="E-Class",
        year=2023,
        price="150",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="DD 3456 KK",
        color="Grey",
        mileage=12800,
        description=(
            "A 2023 E 220 d with an automatic gearbox. The traditional executive sedan: "
            "long doors, a quiet diesel, and a cabin built for distance."
        ),
        must=["e-class", "e class", "e 220", "e220", "w214", "w213"],
        reject=["s-class", "c-class", "gle", "glc", "cls"],
        any_must=True,
    ),
    _car(
        slug="audi-a6",
        brand="Audi",
        model="A6",
        year=2022,
        price="130",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Premium",
        plate="KA 2420 IK",
        color="Grey",
        mileage=24100,
        description=(
            "A 2022 A6 45 TFSI, a 2.0-litre petrol with an automatic gearbox. "
            "A formal sedan with the space of a proper executive car."
        ),
        must=["a6"],
        reject=["a6 allroad", "rs6", "s6", "a4", "a8", "a7", "q7", "q8"],
    ),
    _car(
        slug="bmw-7-series",
        brand="BMW",
        model="7 Series",
        year=2023,
        price="208",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Premium",
        plate="KA 2421 IK",
        color="Black",
        mileage=8900,
        description=(
            "A 2023 740i with the 3.0-litre petrol engine and an automatic gearbox. "
            "A chauffeur-style sedan with a lounge rear seat."
        ),
        must=["7 series", "740i", "740"],
        reject=["5 series", "3 series", "x7", "i7", "m760"],
        any_must=True,
    ),
    _car(
        slug="mercedes-s-class",
        brand="Mercedes-Benz",
        model="S-Class",
        year=2022,
        price="236",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Premium",
        plate="KA 2422 IK",
        color="Black",
        mileage=16400,
        description=(
            "A 2022 S 500 with the 3.0-litre petrol engine and an automatic gearbox. "
            "The flagship sedan in the fleet, for airport transfers and long evenings."
        ),
        must=["s-class", "s class", "s 500", "s500", "w223"],
        reject=["e-class", "c-class", "gls", "amg gt", "sl "],
        any_must=True,
    ),
    _car(
        slug="toyota-rav4",
        brand="Toyota",
        model="RAV4",
        year=2023,
        price="68",
        seats=5,
        transmission="Automatic",
        fuel="Hybrid",
        car_class="Comfort",
        plate="KA 2423 IK",
        color="Green",
        mileage=19800,
        description=(
            "A 2023 RAV4 hybrid with an automatic gearbox. A high-sitting crossover "
            "for a family week without stepping up to a luxury SUV."
        ),
        must=["rav4", "rav 4"],
        reject=["prime"],
        any_must=True,
    ),
    _car(
        slug="bmw-x5",
        brand="BMW",
        model="X5",
        year=2022,
        price="126",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2424 IK",
        color="Black",
        mileage=31200,
        description=(
            "A 2022 X5 xDrive30d, a 3.0-litre diesel with an automatic gearbox. "
            "A large premium SUV, separate from the X5 M already in the garage."
        ),
        must=["x5"],
        reject=["x5 m", "x3", "x6", "x7", "ix5", "m50"],
    ),
    _car(
        slug="mercedes-glc",
        brand="Mercedes-Benz",
        model="GLC",
        year=2023,
        price="98",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2425 IK",
        color="Silver",
        mileage=14700,
        description=(
            "A 2023 GLC 220 d with an automatic gearbox. A mid-size Mercedes SUV "
            "that is easier to place than the larger GLE."
        ),
        must=["glc"],
        reject=["gle", "gls", "glb", "gla", "amg"],
    ),
    _car(
        slug="audi-q5",
        brand="Audi",
        model="Q5",
        year=2022,
        price="104",
        seats=5,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2426 IK",
        color="Grey",
        mileage=26900,
        description=(
            "A 2022 Q5 40 TDI, a 2.0-litre diesel with an automatic gearbox. "
            "A premium crossover for five people and a full boot."
        ),
        must=["q5"],
        reject=["sq5", "q5 e-tron", "q3", "q7", "q8", "rs q5"],
    ),
    _car(
        slug="hyundai-tucson",
        brand="Hyundai",
        model="Tucson",
        year=2023,
        price="62",
        seats=5,
        transmission="Automatic",
        fuel="Hybrid",
        car_class="Comfort",
        plate="FF 1122 KK",
        color="Red",
        mileage=17600,
        description=(
            "A 2023 Tucson hybrid with an automatic gearbox. A family crossover "
            "with a high seat and a calm hybrid drivetrain."
        ),
        must=["tucson"],
        reject=["santa fe", "ioniq"],
    ),
    _car(
        slug="kia-sportage",
        brand="Kia",
        model="Sportage",
        year=2023,
        price="58",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Comfort",
        plate="HH 5566 KK",
        color="Green",
        mileage=20300,
        description=(
            "A 2023 Sportage 1.6 T-GDI petrol with an automatic gearbox. "
            "A current-shape crossover for five, with a wide boot."
        ),
        must=["sportage"],
        reject=["sorento", "ev6", "niro"],
    ),
    _car(
        slug="volvo-xc60",
        brand="Volvo",
        model="XC60",
        year=2022,
        price="118",
        seats=5,
        transmission="Automatic",
        fuel="Hybrid",
        car_class="Premium",
        plate="KA 2429 IK",
        color="Grey",
        mileage=22800,
        description=(
            "A 2022 XC60 T6 plug-in hybrid with an automatic gearbox. "
            "It can run short trips on the battery and still take a highway day on petrol."
        ),
        must=["xc60"],
        reject=["xc90", "xc40", "s60"],
    ),
    _car(
        slug="porsche-cayenne",
        brand="Porsche",
        model="Cayenne",
        year=2021,
        price="154",
        seats=5,
        transmission="Automatic",
        fuel="Gasoline",
        car_class="Premium",
        plate="KA 2430 IK",
        color="Black",
        mileage=34100,
        description=(
            "A 2021 Cayenne with the 3.0-litre petrol engine and an automatic gearbox. "
            "A tall Porsche for five people who still want a sports-car steering feel."
        ),
        must=["cayenne"],
        reject=["cayenne coupe", "turbo s", "macan", "panamera"],
    ),
    _car(
        slug="tesla-model-3",
        brand="Tesla",
        model="Model 3",
        year=2023,
        price="82",
        seats=5,
        transmission="Automatic",
        fuel="Electric",
        car_class="Comfort",
        plate="KA 2431 IK",
        color="White",
        mileage=21400,
        description=(
            "A 2023 Model 3 Long Range. Rear-drive electric sedan, no combustion engine, "
            "with a battery in the mid-70 kWh class and an automatic single-speed drive."
        ),
        must=["model 3", "model3"],
        reject=["model y", "model s", "model x", "cybertruck"],
        any_must=True,
    ),
    _car(
        slug="tesla-model-y",
        brand="Tesla",
        model="Model Y",
        year=2024,
        price="94",
        seats=5,
        transmission="Automatic",
        fuel="Electric",
        car_class="Comfort",
        plate="KA 2432 IK",
        color="Blue",
        mileage=8200,
        description=(
            "A 2024 Model Y Long Range. An electric crossover with a higher roof than the Model 3 "
            "and a single-speed drive, not a petrol engine."
        ),
        must=["model y", "modely"],
        reject=["model 3", "model s", "model x"],
        any_must=True,
    ),
    _car(
        slug="bmw-i4",
        brand="BMW",
        model="i4",
        year=2023,
        price="108",
        seats=5,
        transmission="Automatic",
        fuel="Electric",
        car_class="Premium",
        plate="KA 2433 IK",
        color="Grey",
        mileage=13500,
        description=(
            "A 2023 i4 eDrive40. A battery-electric gran coupe with a single-speed drive "
            "and no engine displacement to quote."
        ),
        must=["i4"],
        reject=["i3", "i7", "i5", "ix ", "4 series"],
    ),
    _car(
        slug="hyundai-ioniq-5",
        brand="Hyundai",
        model="IONIQ 5",
        year=2023,
        price="90",
        seats=5,
        transmission="Automatic",
        fuel="Electric",
        car_class="Comfort",
        plate="KA 2434 IK",
        color="Grey",
        mileage=16200,
        description=(
            "A 2023 IONIQ 5 Long Range. A flat-floor electric hatchback with a single-speed drive "
            "and a battery large enough for a day between charges."
        ),
        must=["ioniq 5", "ioniq5"],
        reject=["ioniq 6", "ioniq6", "ioniq electric"],
        any_must=True,
    ),
    _car(
        slug="kia-ev6",
        brand="Kia",
        model="EV6",
        year=2023,
        price="86",
        seats=5,
        transmission="Automatic",
        fuel="Electric",
        car_class="Comfort",
        plate="KA 2435 IK",
        color="Green",
        mileage=14900,
        description=(
            "A 2023 EV6 Long Range. An electric crossover with a single-speed drive "
            "and a low nose, not a turbo petrol."
        ),
        must=["ev6"],
        reject=["ev9", "niro", "sportage"],
    ),
    _car(
        slug="porsche-taycan",
        brand="Porsche",
        model="Taycan",
        year=2022,
        price="140",
        seats=4,
        transmission="Automatic",
        fuel="Electric",
        car_class="Premium",
        plate="KA 2436 IK",
        color="White",
        mileage=11800,
        description=(
            "A 2022 Taycan. Porsche's battery-electric sedan, with a two-speed rear drive "
            "and no combustion engine. Four seats in this fleet car."
        ),
        must=["taycan"],
        reject=["turbo s", "cross turismo", "sport turismo", "panamera", "cayenne"],
    ),
    _car(
        slug="volkswagen-touran",
        brand="Volkswagen",
        model="Touran",
        year=2021,
        price="52",
        seats=7,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Comfort",
        plate="KA 2437 IK",
        color="Silver",
        mileage=58700,
        description=(
            "A 2021 Touran 2.0 TDI with an automatic gearbox and seven seats. "
            "A compact people-mover for a family that has outgrown a hatchback."
        ),
        must=["touran"],
        reject=["touareg", "tiguan"],
    ),
    _car(
        slug="ford-s-max",
        brand="Ford",
        model="S-Max",
        year=2020,
        price="54",
        seats=7,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Comfort",
        plate="KA 2438 IK",
        color="Blue",
        mileage=72400,
        description=(
            "A 2020 S-Max 2.0 TDCi with an automatic gearbox and seven seats. "
            "Lower and longer than a van, built for seven and a holiday load."
        ),
        must=["s-max", "s max"],
        reject=["galaxy", "c-max", "focus"],
        any_must=True,
    ),
    _car(
        slug="mercedes-v-class",
        brand="Mercedes-Benz",
        model="V-Class",
        year=2022,
        price="112",
        seats=7,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2439 IK",
        color="Black",
        mileage=39600,
        description=(
            "A 2022 V 220 d with an automatic gearbox and seven seats. "
            "A business van with captain's chairs rather than a bench."
        ),
        must=["v-class", "v class", "v 220", "v220", "viano"],
        reject=["vito", "sprinter", "g-class", "e-class"],
        any_must=True,
    ),
    _car(
        slug="volkswagen-multivan",
        brand="Volkswagen",
        model="Multivan",
        year=2023,
        price="126",
        seats=7,
        transmission="Automatic",
        fuel="Diesel",
        car_class="Premium",
        plate="KA 2440 IK",
        color="White",
        mileage=18900,
        description=(
            "A 2023 Multivan 2.0 TDI with an automatic gearbox and seven seats. "
            "The current van, with a flat floor and sliding doors on both sides."
        ),
        must=["multivan"],
        reject=["california", "caravelle", "transporter", "id. buzz", "crafter", "t5", "t4", "t6"],
    ),
)

# Old demo cars with no bookings. The manually added BMW X5M is not in this list.
RETIRED_PLATES = ("AA 1234 KK", "CC 9012 KK")

PHOTO_FILES = {
    "front": "01_front.webp",
    "rear": "02_rear.webp",
    "interior": "03_interior.webp",
}
