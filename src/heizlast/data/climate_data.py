"""Klimadaten nach DIN EN 12831-1 für deutsche Standorte."""

from __future__ import annotations

from ..models.climate import ClimateData


def apply_altitude_correction(theta_e_ref: float, altitude_ref: float, altitude_build: float) -> float:
    """Höhenkorrektur nach DIN EN 12831-1 §6.3.7.
    
    Args:
        theta_e_ref: Auslegungsaußentemperatur in °C
        altitude_ref: Referenzhöhe in m
        altitude_build: Standorthöhe in m
    
    Returns:
        Korrigierte Auslegungsaußentemperatur in °C
    """
    diff = altitude_build - altitude_ref
    if abs(diff) >= 200.0:
        return theta_e_ref + (-0.01) * diff
    return theta_e_ref


CLIMATE_DATA: dict[str, ClimateData] = {
    # Baden-Württemberg
    "79098": ClimateData(plz="79098", location="Freiburg im Breisgau", theta_e_ref=-12.0, theta_e_mean=10.5, altitude_ref=278.0),
    "76133": ClimateData(plz="76133", location="Karlsruhe", theta_e_ref=-11.0, theta_e_mean=10.2, altitude_ref=119.0),
    "70173": ClimateData(plz="70173", location="Stuttgart", theta_e_ref=-12.0, theta_e_mean=9.7, altitude_ref=260.0),
    "89073": ClimateData(plz="89073", location="Ulm", theta_e_ref=-13.0, theta_e_mean=9.0, altitude_ref=478.0),
    "78462": ClimateData(plz="78462", location="Konstanz", theta_e_ref=-11.0, theta_e_mean=9.8, altitude_ref=400.0),
    "68159": ClimateData(plz="68159", location="Mannheim", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=98.0),
    "72764": ClimateData(plz="72764", location="Reutlingen", theta_e_ref=-12.0, theta_e_mean=8.8, altitude_ref=350.0),
    "73525": ClimateData(plz="73525", location="Schwäbisch Gmünd", theta_e_ref=-12.0, theta_e_mean=9.0, altitude_ref=320.0),
    "75172": ClimateData(plz="75172", location="Pforzheim", theta_e_ref=-11.0, theta_e_mean=9.8, altitude_ref=265.0),
    "88212": ClimateData(plz="88212", location="Ravensburg", theta_e_ref=-13.0, theta_e_mean=8.5, altitude_ref=475.0),
    "71634": ClimateData(plz="71634", location="Ludwigsburg", theta_e_ref=-12.0, theta_e_mean=9.5, altitude_ref=230.0),
    "73728": ClimateData(plz="73728", location="Esslingen am Neckar", theta_e_ref=-12.0, theta_e_mean=9.6, altitude_ref=235.0),
    "78048": ClimateData(plz="78048", location="Villingen-Schwenningen", theta_e_ref=-14.0, theta_e_mean=7.5, altitude_ref=700.0),
    "78628": ClimateData(plz="78628", location="Rottweil", theta_e_ref=-13.0, theta_e_mean=8.0, altitude_ref=560.0),
    "72458": ClimateData(plz="72458", location="Albstadt", theta_e_ref=-13.0, theta_e_mean=7.8, altitude_ref=740.0),
    
    # Bayern
    "80331": ClimateData(plz="80331", location="München", theta_e_ref=-13.0, theta_e_mean=8.7, altitude_ref=520.0),
    "90402": ClimateData(plz="90402", location="Nürnberg", theta_e_ref=-13.0, theta_e_mean=9.0, altitude_ref=320.0),
    "86150": ClimateData(plz="86150", location="Augsburg", theta_e_ref=-13.0, theta_e_mean=8.8, altitude_ref=490.0),
    "93047": ClimateData(plz="93047", location="Regensburg", theta_e_ref=-13.0, theta_e_mean=9.0, altitude_ref=350.0),
    "97070": ClimateData(plz="97070", location="Würzburg", theta_e_ref=-12.0, theta_e_mean=9.7, altitude_ref=180.0),
    "95444": ClimateData(plz="95444", location="Bayreuth", theta_e_ref=-14.0, theta_e_mean=8.3, altitude_ref=350.0),
    "85049": ClimateData(plz="85049", location="Ingolstadt", theta_e_ref=-13.0, theta_e_mean=8.8, altitude_ref=380.0),
    "97421": ClimateData(plz="97421", location="Schweinfurt", theta_e_ref=-12.0, theta_e_mean=9.4, altitude_ref=220.0),
    "92224": ClimateData(plz="92224", location="Amberg", theta_e_ref=-14.0, theta_e_mean=8.5, altitude_ref=400.0),
    "94032": ClimateData(plz="94032", location="Passau", theta_e_ref=-14.0, theta_e_mean=8.5, altitude_ref=300.0),
    "87437": ClimateData(plz="87437", location="Kempten (Allgäu)", theta_e_ref=-15.0, theta_e_mean=7.0, altitude_ref=710.0),
    "82362": ClimateData(plz="82362", location="Weilheim in Oberbayern", theta_e_ref=-14.0, theta_e_mean=7.5, altitude_ref=560.0),
    "92637": ClimateData(plz="92637", location="Weiden in der Oberpfalz", theta_e_ref=-14.0, theta_e_mean=8.0, altitude_ref=425.0),
    "84160": ClimateData(plz="84160", location="Landshut", theta_e_ref=-13.0, theta_e_mean=8.5, altitude_ref=385.0),
    "96450": ClimateData(plz="96450", location="Coburg", theta_e_ref=-13.0, theta_e_mean=8.6, altitude_ref=290.0),
    
    # Berlin
    "10115": ClimateData(plz="10115", location="Berlin-Mitte", theta_e_ref=-11.0, theta_e_mean=9.9, altitude_ref=35.0),
    "12043": ClimateData(plz="12043", location="Berlin-Neukölln", theta_e_ref=-11.0, theta_e_mean=9.9, altitude_ref=38.0),
    "13585": ClimateData(plz="13585", location="Berlin-Spandau", theta_e_ref=-11.0, theta_e_mean=9.8, altitude_ref=32.0),
    
    # Brandenburg
    "14467": ClimateData(plz="14467", location="Potsdam", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=40.0),
    "15230": ClimateData(plz="15230", location="Frankfurt (Oder)", theta_e_ref=-12.0, theta_e_mean=9.3, altitude_ref=35.0),
    "03046": ClimateData(plz="03046", location="Cottbus", theta_e_ref=-12.0, theta_e_mean=9.2, altitude_ref=70.0),
    
    # Bremen
    "28195": ClimateData(plz="28195", location="Bremen", theta_e_ref=-10.0, theta_e_mean=9.8, altitude_ref=5.0),
    
    # Hamburg
    "20095": ClimateData(plz="20095", location="Hamburg-Altstadt", theta_e_ref=-10.0, theta_e_mean=9.5, altitude_ref=5.0),
    "22081": ClimateData(plz="22081", location="Hamburg-Winterhude", theta_e_ref=-10.0, theta_e_mean=9.5, altitude_ref=8.0),
    
    # Hessen
    "60311": ClimateData(plz="60311", location="Frankfurt am Main", theta_e_ref=-10.0, theta_e_mean=10.2, altitude_ref=112.0),
    "65185": ClimateData(plz="65185", location="Wiesbaden", theta_e_ref=-10.0, theta_e_mean=10.1, altitude_ref=150.0),
    "34117": ClimateData(plz="34117", location="Kassel", theta_e_ref=-12.0, theta_e_mean=8.9, altitude_ref=165.0),
    "64283": ClimateData(plz="64283", location="Darmstadt", theta_e_ref=-10.0, theta_e_mean=10.2, altitude_ref=150.0),
    "35510": ClimateData(plz="35510", location="Butzbach", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=200.0),
    "61118": ClimateData(plz="61118", location="Bad Vilbel", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=130.0),
    "64347": ClimateData(plz="64347", location="Griesheim", theta_e_ref=-10.0, theta_e_mean=10.1, altitude_ref=105.0),
    "61348": ClimateData(plz="61348", location="Bad Homburg vor der Höhe", theta_e_ref=-11.0, theta_e_mean=9.8, altitude_ref=210.0),
    "64331": ClimateData(plz="64331", location="Weiterstadt", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=140.0),
    "63065": ClimateData(plz="63065", location="Hanau", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=108.0),
    "34121": ClimateData(plz="34121", location="Kassel", theta_e_ref=-12.0, theta_e_mean=8.9, altitude_ref=165.0),
    "35390": ClimateData(plz="35390", location="Gießen", theta_e_ref=-11.0, theta_e_mean=9.1, altitude_ref=180.0),
    "67547": ClimateData(plz="67547", location="Worms", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=95.0),
    "67549": ClimateData(plz="67549", location="Worms", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=100.0),
    "65001": ClimateData(plz="65001", location="Wiesbaden", theta_e_ref=-10.0, theta_e_mean=10.1, altitude_ref=150.0),
    "65203": ClimateData(plz="65203", location="Wiesbaden", theta_e_ref=-10.0, theta_e_mean=10.1, altitude_ref=140.0),
    "65510": ClimateData(plz="65510", location="Idstein", theta_e_ref=-11.0, theta_e_mean=9.2, altitude_ref=300.0),
    "65719": ClimateData(plz="65719", location="Hofheim am Taunus", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=150.0),
    
    # Mecklenburg-Vorpommern
    "18055": ClimateData(plz="18055", location="Rostock", theta_e_ref=-10.0, theta_e_mean=9.1, altitude_ref=10.0),
    "18435": ClimateData(plz="18435", location="Stralsund", theta_e_ref=-10.0, theta_e_mean=9.0, altitude_ref=8.0),
    "19053": ClimateData(plz="19053", location="Schwerin", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=40.0),
    "17335": ClimateData(plz="17335", location="Neubrandenburg", theta_e_ref=-11.0, theta_e_mean=8.5, altitude_ref=65.0),
    "17489": ClimateData(plz="17489", location="Greifswald", theta_e_ref=-10.0, theta_e_mean=9.0, altitude_ref=5.0),
    
    # Niedersachsen
    "30159": ClimateData(plz="30159", location="Hannover", theta_e_ref=-11.0, theta_e_mean=9.7, altitude_ref=55.0),
    "38100": ClimateData(plz="38100", location="Braunschweig", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=85.0),
    "26122": ClimateData(plz="26122", location="Oldenburg (Oldenburg)", theta_e_ref=-9.0, theta_e_mean=9.5, altitude_ref=5.0),
    "49074": ClimateData(plz="49074", location="Osnabrück", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=50.0),
    "21335": ClimateData(plz="21335", location="Lüneburg", theta_e_ref=-10.0, theta_e_mean=9.5, altitude_ref=20.0),
    "27568": ClimateData(plz="27568", location="Bremerhaven", theta_e_ref=-9.0, theta_e_mean=9.5, altitude_ref=3.0),
    "29525": ClimateData(plz="29525", location="Uelzen", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=40.0),
    "31535": ClimateData(plz="31535", location="Neustadt am Rübenberge", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=40.0),
    "31655": ClimateData(plz="31655", location="Stadthagen", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=60.0),
    "21702": ClimateData(plz="21702", location="Stade", theta_e_ref=-10.0, theta_e_mean=9.5, altitude_ref=10.0),
    "26316": ClimateData(plz="26316", location="Varel", theta_e_ref=-9.0, theta_e_mean=9.5, altitude_ref=5.0),
    "26506": ClimateData(plz="26506", location="Norden", theta_e_ref=-9.0, theta_e_mean=9.5, altitude_ref=3.0),
    "26789": ClimateData(plz="26789", location="Leer (Ostfriesland)", theta_e_ref=-9.0, theta_e_mean=9.5, altitude_ref=2.0),
    "27432": ClimateData(plz="27432", location="Bremervörde", theta_e_ref=-10.0, theta_e_mean=9.5, altitude_ref=5.0),
    "29614": ClimateData(plz="29614", location="Soltau", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=35.0),
    "31737": ClimateData(plz="31737", location="Rinteln", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=50.0),
    "37520": ClimateData(plz="37520", location="Höxter", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=95.0),
    "29633": ClimateData(plz="29633", location="Munster", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=70.0),
    "37073": ClimateData(plz="37073", location="Göttingen", theta_e_ref=-12.0, theta_e_mean=9.0, altitude_ref=150.0),
    
    # Nordrhein-Westfalen
    "50667": ClimateData(plz="50667", location="Köln", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=45.0),
    "40210": ClimateData(plz="40210", location="Düsseldorf", theta_e_ref=-10.0, theta_e_mean=10.6, altitude_ref=38.0),
    "44137": ClimateData(plz="44137", location="Dortmund", theta_e_ref=-11.0, theta_e_mean=9.8, altitude_ref=85.0),
    "45127": ClimateData(plz="45127", location="Essen", theta_e_ref=-10.0, theta_e_mean=10.1, altitude_ref=40.0),
    "53111": ClimateData(plz="53111", location="Bonn", theta_e_ref=-10.0, theta_e_mean=10.4, altitude_ref=60.0),
    "52062": ClimateData(plz="52062", location="Aachen", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=175.0),
    "48143": ClimateData(plz="48143", location="Münster", theta_e_ref=-10.0, theta_e_mean=9.9, altitude_ref=60.0),
    "33098": ClimateData(plz="33098", location="Paderborn", theta_e_ref=-11.0, theta_e_mean=9.3, altitude_ref=115.0),
    "58636": ClimateData(plz="58636", location="Iserlohn", theta_e_ref=-12.0, theta_e_mean=9.0, altitude_ref=250.0),
    "58095": ClimateData(plz="58095", location="Hagen", theta_e_ref=-11.0, theta_e_mean=9.6, altitude_ref=130.0),
    "59494": ClimateData(plz="59494", location="Soest", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=80.0),
    "49076": ClimateData(plz="49076", location="Osnabrück", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=50.0),
    "41061": ClimateData(plz="41061", location="Mönchengladbach", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=70.0),
    "42103": ClimateData(plz="42103", location="Wuppertal", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=170.0),
    "44787": ClimateData(plz="44787", location="Bochum", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=80.0),
    "45879": ClimateData(plz="45879", location="Gelsenkirchen", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=60.0),
    "46047": ClimateData(plz="46047", location="Oberhausen", theta_e_ref=-10.0, theta_e_mean=10.2, altitude_ref=35.0),
    "47053": ClimateData(plz="47053", location="Duisburg", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=30.0),
    "50733": ClimateData(plz="50733", location="Köln", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=45.0),
    "50968": ClimateData(plz="50968", location="Köln", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=50.0),
    "52070": ClimateData(plz="52070", location="Aachen", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=175.0),
    "53173": ClimateData(plz="53173", location="Bonn", theta_e_ref=-10.0, theta_e_mean=10.4, altitude_ref=60.0),
    "53179": ClimateData(plz="53179", location="Bonn", theta_e_ref=-10.0, theta_e_mean=10.4, altitude_ref=65.0),
    "57223": ClimateData(plz="57223", location="Kreuzau", theta_e_ref=-10.0, theta_e_mean=9.8, altitude_ref=200.0),
    "53859": ClimateData(plz="53859", location="Niederkassel", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=55.0),
    "50226": ClimateData(plz="50226", location="Frechen", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=50.0),
    "51503": ClimateData(plz="51503", location="Rösrath", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=100.0),
    "51519": ClimateData(plz="51519", location="Odenthal", theta_e_ref=-10.0, theta_e_mean=9.8, altitude_ref=130.0),
    "51702": ClimateData(plz="51702", location="Bergneustadt", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=350.0),
    "53840": ClimateData(plz="53840", location="Troisdorf", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=60.0),
    "53902": ClimateData(plz="53902", location="Bad Münstereifel", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=320.0),
    "55288": ClimateData(plz="55288", location="Oppenheim", theta_e_ref=-10.0, theta_e_mean=10.5, altitude_ref=100.0),
    
    # Rheinland-Pfalz
    "55116": ClimateData(plz="55116", location="Mainz", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=90.0),
    "54290": ClimateData(plz="54290", location="Trier", theta_e_ref=-11.0, theta_e_mean=9.7, altitude_ref=130.0),
    "67059": ClimateData(plz="67059", location="Ludwigshafen am Rhein", theta_e_ref=-10.0, theta_e_mean=10.3, altitude_ref=95.0),
    "56068": ClimateData(plz="56068", location="Koblenz", theta_e_ref=-10.0, theta_e_mean=10.0, altitude_ref=70.0),
    "67433": ClimateData(plz="67433", location="Speyer", theta_e_ref=-10.0, theta_e_mean=10.4, altitude_ref=95.0),
    "76829": ClimateData(plz="76829", location="Landau in der Pfalz", theta_e_ref=-10.0, theta_e_mean=10.2, altitude_ref=125.0),
    "54550": ClimateData(plz="54550", location="Daun", theta_e_ref=-12.0, theta_e_mean=8.0, altitude_ref=420.0),
    "55442": ClimateData(plz="55442", location="Simmern/Hunsrück", theta_e_ref=-11.0, theta_e_mean=9.2, altitude_ref=310.0),
    "56281": ClimateData(plz="56281", location="Emmelshausen", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=350.0),
    "67700": ClimateData(plz="67700", location="Kaiserslautern", theta_e_ref=-11.0, theta_e_mean=9.3, altitude_ref=270.0),
    "66953": ClimateData(plz="66953", location="Pirmasens", theta_e_ref=-11.0, theta_e_mean=9.0, altitude_ref=250.0),
    "66740": ClimateData(plz="66740", location="Saarlouis", theta_e_ref=-11.0, theta_e_mean=9.7, altitude_ref=190.0),
    
    # Saarland
    "66111": ClimateData(plz="66111", location="Saarbrücken", theta_e_ref=-11.0, theta_e_mean=9.8, altitude_ref=230.0),
    "66538": ClimateData(plz="66538", location="Neunkirchen", theta_e_ref=-11.0, theta_e_mean=9.5, altitude_ref=260.0),
    "66606": ClimateData(plz="66606", location="St. Wendel", theta_e_ref=-12.0, theta_e_mean=9.0, altitude_ref=320.0),
    
    # Sachsen
    "01067": ClimateData(plz="01067", location="Dresden", theta_e_ref=-12.0, theta_e_mean=9.3, altitude_ref=120.0),
    "04109": ClimateData(plz="04109", location="Leipzig", theta_e_ref=-12.0, theta_e_mean=9.6, altitude_ref=115.0),
    "09111": ClimateData(plz="09111", location="Chemnitz", theta_e_ref=-13.0, theta_e_mean=8.6, altitude_ref=300.0),
    "08056": ClimateData(plz="08056", location="Zwickau", theta_e_ref=-13.0, theta_e_mean=8.5, altitude_ref=270.0),
    "02625": ClimateData(plz="02625", location="Bautzen", theta_e_ref=-13.0, theta_e_mean=8.8, altitude_ref=200.0),
    "01809": ClimateData(plz="01809", location="Dohna", theta_e_ref=-12.0, theta_e_mean=9.0, altitude_ref=190.0),
    "09557": ClimateData(plz="09557", location="Flöha", theta_e_ref=-13.0, theta_e_mean=8.3, altitude_ref=350.0),
    "08340": ClimateData(plz="08340", location="Hohenstein-Ernstthal", theta_e_ref=-13.0, theta_e_mean=8.3, altitude_ref=360.0),
    
    # Sachsen-Anhalt
    "39104": ClimateData(plz="39104", location="Magdeburg", theta_e_ref=-12.0, theta_e_mean=9.5, altitude_ref=50.0),
    "06108": ClimateData(plz="06108", location="Halle (Saale)", theta_e_ref=-12.0, theta_e_mean=9.4, altitude_ref=90.0),
    "06844": ClimateData(plz="06844", location="Dessau-Roßlau", theta_e_ref=-12.0, theta_e_mean=9.5, altitude_ref=70.0),
    "38855": ClimateData(plz="38855", location="Wernigerode", theta_e_ref=-13.0, theta_e_mean=8.0, altitude_ref=270.0),
    "06667": ClimateData(plz="06667", location="Weißenfels", theta_e_ref=-12.0, theta_e_mean=9.3, altitude_ref=130.0),
    "38875": ClimateData(plz="38875", location="Blankenburg (Harz)", theta_e_ref=-13.0, theta_e_mean=7.8, altitude_ref=230.0),
    "39288": ClimateData(plz="39288", location="Burg", theta_e_ref=-12.0, theta_e_mean=9.4, altitude_ref=60.0),
    "06369": ClimateData(plz="06369", location="Seeland", theta_e_ref=-12.0, theta_e_mean=9.0, altitude_ref=160.0),
    
    # Schleswig-Holstein
    "24103": ClimateData(plz="24103", location="Kiel", theta_e_ref=-9.0, theta_e_mean=9.0, altitude_ref=5.0),
    "23552": ClimateData(plz="23552", location="Lübeck", theta_e_ref=-9.0, theta_e_mean=9.2, altitude_ref=10.0),
    "24937": ClimateData(plz="24937", location="Flensburg", theta_e_ref=-9.0, theta_e_mean=8.8, altitude_ref=5.0),
    "24837": ClimateData(plz="24837", location="Schleswig", theta_e_ref=-9.0, theta_e_mean=9.0, altitude_ref=8.0),
    "25746": ClimateData(plz="25746", location="Heide", theta_e_ref=-9.0, theta_e_mean=9.0, altitude_ref=5.0),
    "25938": ClimateData(plz="25938", location="Wrixum/Föhr", theta_e_ref=-8.0, theta_e_mean=8.8, altitude_ref=2.0),
    "25813": ClimateData(plz="25813", location="Husum", theta_e_ref=-9.0, theta_e_mean=9.0, altitude_ref=3.0),
    "25761": ClimateData(plz="25761", location="Büsum", theta_e_ref=-8.0, theta_e_mean=9.2, altitude_ref=2.0),
    "23701": ClimateData(plz="23701", location="Eutin", theta_e_ref=-9.0, theta_e_mean=9.0, altitude_ref=30.0),
    "24534": ClimateData(plz="24534", location="Neumünster", theta_e_ref=-10.0, theta_e_mean=9.2, altitude_ref=25.0),
    "24782": ClimateData(plz="24782", location="Bordesholm", theta_e_ref=-10.0, theta_e_mean=9.2, altitude_ref=30.0),
    "25524": ClimateData(plz="25524", location="Itzehoe", theta_e_ref=-9.0, theta_e_mean=9.2, altitude_ref=10.0),
    "27474": ClimateData(plz="27474", location="Cuxhaven", theta_e_ref=-9.0, theta_e_mean=9.3, altitude_ref=2.0),
    
    # Thüringen
    "99084": ClimateData(plz="99084", location="Erfurt", theta_e_ref=-13.0, theta_e_mean=8.7, altitude_ref=195.0),
    "07743": ClimateData(plz="07743", location="Jena", theta_e_ref=-13.0, theta_e_mean=8.8, altitude_ref=160.0),
    "99096": ClimateData(plz="99096", location="Gotha", theta_e_ref=-13.0, theta_e_mean=8.3, altitude_ref=260.0),
    "99867": ClimateData(plz="99867", location="Gotha", theta_e_ref=-13.0, theta_e_mean=8.3, altitude_ref=260.0),
    "07545": ClimateData(plz="07545", location="Gera", theta_e_ref=-13.0, theta_e_mean=8.7, altitude_ref=205.0),
    "98527": ClimateData(plz="98527", location="Eisenach", theta_e_ref=-13.0, theta_e_mean=8.4, altitude_ref=230.0),
    "98617": ClimateData(plz="98617", location="Meiningen", theta_e_ref=-14.0, theta_e_mean=7.8, altitude_ref=320.0),
    "07907": ClimateData(plz="07907", location="Schleiz", theta_e_ref=-13.0, theta_e_mean=8.0, altitude_ref=430.0),
    "04600": ClimateData(plz="04600", location="Altenburg", theta_e_ref=-13.0, theta_e_mean=9.0, altitude_ref=200.0),
    "99310": ClimateData(plz="99310", location="Arnstadt", theta_e_ref=-13.0, theta_e_mean=8.4, altitude_ref=280.0),
    "98701": ClimateData(plz="98701", location="Grossbreitenbach", theta_e_ref=-14.0, theta_e_mean=7.5, altitude_ref=560.0),
    "07952": ClimateData(plz="07952", location="Pausa-Mühltroff", theta_e_ref=-13.0, theta_e_mean=8.0, altitude_ref=380.0),
    
    # Niedersachsen - weitere Städte
    "38440": ClimateData(plz="38440", location="Wolfsburg", theta_e_ref=-11.7, theta_e_mean=9.6, altitude_ref=80.0),
    "38001": ClimateData(plz="38001", location="Salzgitter", theta_e_ref=-11.0, theta_e_mean=9.3, altitude_ref=130.0),
    "38448": ClimateData(plz="38448", location="Wolfsburg", theta_e_ref=-11.7, theta_e_mean=9.6, altitude_ref=80.0),
    "38442": ClimateData(plz="38442", location="Wolfsburg", theta_e_ref=-11.7, theta_e_mean=9.6, altitude_ref=85.0),
    "38444": ClimateData(plz="38444", location="Wolfsburg", theta_e_ref=-11.7, theta_e_mean=9.6, altitude_ref=82.0),
    "38446": ClimateData(plz="38446", location="Wolfsburg", theta_e_ref=-11.7, theta_e_mean=9.6, altitude_ref=78.0),
}


def get_climate_data(plz: str) -> ClimateData | None:
    """Sucht Klimadaten für eine Postleitzahl.
    
    Args:
        plz: 5-stellige Postleitzahl
    
    Returns:
        ClimateData-Objekt oder None, falls keine Daten gefunden
    """
    # Exakte PLZ-Suche
    if plz in CLIMATE_DATA:
        return CLIMATE_DATA[plz]
    
    # Fallback: Suche nach PLZ-Präfix (erste 4 Stellen)
    plz_prefix_4 = plz[:4]
    for key, data in CLIMATE_DATA.items():
        if key.startswith(plz_prefix_4):
            return data
    
    # Fallback: Suche nach PLZ-Präfix (erste 3 Stellen)
    plz_prefix_3 = plz[:3]
    for key, data in CLIMATE_DATA.items():
        if key.startswith(plz_prefix_3):
            return data
    
    # Fallback: Suche nach PLZ-Präfix (erste 2 Stellen)
    plz_prefix_2 = plz[:2]
    for key, data in CLIMATE_DATA.items():
        if key.startswith(plz_prefix_2):
            return data
    
    return None
