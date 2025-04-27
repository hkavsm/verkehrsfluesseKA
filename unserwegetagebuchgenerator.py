# Programmieren (HKA Verkehrssystemmanagement), SS 2025
# Gruppe: Arsalan, Ilja, Janusz, Ufuk
# Projekt: Verkehrsflüsse Karlsruhe (Code 1/2)

import pandas as pd
import geopandas as gpd
import numpy as np
import random
import requests
from datetime import timedelta, datetime
from shapely.geometry import Point
from collections import defaultdict

# Seed für Reproduzierbare Ergebnisse
random.seed(432)
np.random.seed(432)

# Parameter
num_people = 1000
min_trips_per_person = 2
max_trips_per_person = 8

print("Starte das Programm...")

# Koordinaten finden (Mapbox-API-Abfrage)
def findlatitude(place):
    try:
        result = requests.get(f'https://api.mapbox.com/search/geocode/v6/forward?q={place}&access_token=pk.eyJ1IjoiaGthdnNtIiwiYSI6ImNtOWpvM2xzdjA0djQydXNiaTJ4bWtnOXYifQ.cBgoMPOQ70fiYOZrBKzDLA&bbox=8.2770,48.9398,8.5441,49.0922&proximity=8.4043,49.0140&autocomplete=false').json()["features"][0]["properties"]["coordinates"]["latitude"]    # siehe Mapbox-API-Documentation, Lon vor Lat
#        result = requests.get(f'https://api.mapbox.com/search/geocode/v6/forward?q={place}&access_token=pk.eyJ1IjoiaGthdnNtIiwiYSI6ImNtOWpvM2xzdjA0djQydXNiaTJ4bWtnOXYifQ.cBgoMPOQ70fiYOZrBKzDLA&bbox=8.4002,49.008,8.4068,49.0104&proximity=8.4043,49.0140').json()["features"][0]["properties"]["coordinates"]["latitude"]
        return result
    except (TypeError, KeyError, IndexError):    # Fehler bei keinem returnten Ergebnis überspringen
        pass

def findlongitude(place):
    try:
        result = requests.get(f'https://api.mapbox.com/search/geocode/v6/forward?q={place}&access_token=pk.eyJ1IjoiaGthdnNtIiwiYSI6ImNtOWpvM2xzdjA0djQydXNiaTJ4bWtnOXYifQ.cBgoMPOQ70fiYOZrBKzDLA&bbox=8.2770,48.9398,8.5441,49.0922&proximity=8.4043,49.0140&autocomplete=false').json()["features"][0]["properties"]["coordinates"]["longitude"]
#        result = requests.get(f'https://api.mapbox.com/search/geocode/v6/forward?q={place}&access_token=pk.eyJ1IjoiaGthdnNtIiwiYSI6ImNtOWpvM2xzdjA0djQydXNiaTJ4bWtnOXYifQ.cBgoMPOQ70fiYOZrBKzDLA&bbox=8.4002,49.008,8.4068,49.0104&proximity=8.4043,49.0140').json()["features"][0]["properties"]["coordinates"]["longitude"]
        return result
    except (TypeError, KeyError, IndexError):    # s.o.
        pass

print("Frage Koordinaten der Locations ab...")

# Beispielwerte für Demografie
ages = np.random.randint(18, 80, size=num_people)
genders = np.random.choice(['männlich', 'weiblich', 'divers'], size=num_people, p=[0.48, 0.48, 0.04])
occupations = ['Schüler*in', 'Student*in', 'Angestellt', 'Selbstständig', 'Rentner*in', 'Arbeitslos']
households = ['alleinlebend', 'Paar ohne Kinder', 'Familie mit Kindern', 'Wohngemeinschaft']
districts = ['Innenstadt', 'Durlach', 'Knielingen', 'Mühlburg', 'Oststadt', 'Südweststadt', 'Neureut', 'Grünwinkel']

locations = [
#    {'Locname': 'KIT Campus Süd', 'Lat': None, 'Lon': None},    # falsch: Südl. Herrenhof (49.009065, 8.400364)
#    {'Locname': 'Marktplatz', 'Lat': None, 'Lon': None},    # falsch (48.999157, 8.471262)
#    {'Locname': 'Hbf', 'Lat': None, 'Lon': None},
#    {'Locname': 'Europabad', 'Lat': None, 'Lon': None},
#    {'Locname': 'ZKM', 'Lat': None, 'Lon': None},
#    {'Locname': 'Schloss Karlsruhe', 'Lat': None, 'Lon': None},    # falsch (48.991166, 8.378708)
    {'Locname': 'Durlach Zentrum', 'Lat': findlatitude('Durlach%20Zentrum'), 'Lon': findlongitude('Durlach%20Zentrum')},
#    {'Locname': 'Wildparkstadion', 'Lat': None, 'Lon': None},
#    {'Locname': 'Rheinhafen', 'Lat': None, 'Lon': None},    # falsch: Rheinhafenstr. (49.003833, 8.340272)
    {'Locname': 'Siemensallee', 'Lat': findlatitude('Siemensallee'), 'Lon': findlongitude('Siemensallee')},
    {'Locname': 'Waldstadt Zentrum', 'Lat': findlatitude('Waldstadt%20Zentrum'), 'Lon': findlongitude('Waldstadt%20Zentrum')},
#    {'Locname': 'Städtisches Klinikum', 'Lat': None, 'Lon': None},
#    {'Locname': 'FH Karlsruhe', 'Lat': None, 'Lon': None},    # falsch: "Karlsruhe" (49.009716, 8.401216)
    {'Locname': 'Rüppurrer Straße', 'Lat': findlatitude('Rüppurrer%20Straße'), 'Lon': findlongitude('Rüppurrer%20Straße')},
    {'Locname': 'Weststadt', 'Lat': findlatitude('Weststadt'), 'Lon': findlongitude('Weststadt')},
    {'Locname': 'Hagsfeld', 'Lat': findlatitude('Hagsfeld'), 'Lon': findlongitude('Hagsfeld')},
#    {'Locname': 'Botanischer Garten', 'Lat': None, 'Lon': None},    # falsch: Gartenstr. (49.004422, 8.388494)
#    {'Locname': 'Turmberg', 'Lat': None, 'Lon': None},    # falsch (49.054125, 8.533004) -- ohne ?autocomplete=false: Turmbergstr. (48.998575, 8.480367)
    {'Locname': 'Günther-Klotz-Anlage', 'Lat': findlatitude('Günther-Klotz-Anlage'), 'Lon': findlongitude('Günther-Klotz-Anlage')},
#    {'Locname': 'Naturkundemuseum Karlsruhe', 'Lat': None, 'Lon': None},    # falsch: "Karlsruhe" (49.009716, 8.401216)
#    {'Locname': 'Staatliche Kunsthalle Karlsruhe', 'Lat': None, 'Lon': None},    # falsch: "Karlsruhe" (49.009716, 8.401216)
    {'Locname': 'Schloss Gottesaue', 'Lat': findlatitude('Schloss%20Gottesaue'), 'Lon': findlongitude('Schloss%20Gottesaue')},    # theoretisch falsch: Am Schloss Gottesaue
    {'Locname': 'Alter Schlachthof', 'Lat': findlatitude('Alter%20Schlachthof'), 'Lon': findlongitude('Alter%20Schlachthof')},
#    {'Locname': 'Majolika Manufaktur', 'Lat': None, 'Lon': None},
    {'Locname': 'Stadtgarten', 'Lat': findlatitude('Stadtgarten'), 'Lon': findlongitude('Stadtgarten')},    # theoretisch falsch: Am Stadtgarten
    {'Locname': 'Schlossplatz', 'Lat': findlatitude('Schlossplatz'), 'Lon': findlongitude('Schlossplatz')},
    {'Locname': 'Friedrichsplatz', 'Lat': findlatitude('Friedrichsplatz'), 'Lon': findlongitude('Friedrichsplatz')},
    {'Locname': 'Ludwigsplatz', 'Lat': findlatitude('Ludwigsplatz'), 'Lon': findlongitude('Ludwigsplatz')},
    {'Locname': 'Kaiserstraße', 'Lat': findlatitude('Kaiserstraße'), 'Lon': findlongitude('Kaiserstraße')},
    {'Locname': 'Karlstraße', 'Lat': findlatitude('Karlstraße'), 'Lon': findlongitude('Karlstraße')},
    {'Locname': 'Erbprinzenstraße', 'Lat': findlatitude('Erbprinzenstraße'), 'Lon': findlongitude('Erbprinzenstraße')},
    {'Locname': 'Kriegsstraße', 'Lat': findlatitude('Kriegsstraße'), 'Lon': findlongitude('Kriegsstraße')},    # ähm 😅 Zum Glück liegt die eine Seite der Kriegsstraße eh in einem anderen Stadtteil als die andere Seite => alles ist erlaubt
    {'Locname': 'Moltkestraße', 'Lat': findlatitude('Moltkestraße'), 'Lon': findlongitude('Moltkestraße')},
    {'Locname': 'Durlacher Allee', 'Lat': findlatitude('Durlacher%20Allee'), 'Lon': findlongitude('Durlacher%20Allee')},
    {'Locname': 'Rüppurrer Straße', 'Lat': findlatitude('Rüppurrer%20Straße'), 'Lon': findlongitude('Rüppurrer%20Straße')},
    {'Locname': 'Herrenstraße', 'Lat': findlatitude('Herrenstraße'), 'Lon': findlongitude('Herrenstraße')},
    {'Locname': 'Waldstraße', 'Lat': findlatitude('Waldstraße'), 'Lon': findlongitude('Waldstraße')},
    {'Locname': 'Sophienstraße', 'Lat': findlatitude('Sophienstraße'), 'Lon': findlongitude('Sophienstraße')},
    {'Locname': 'Kanalweg', 'Lat': findlatitude('Kanalweg'), 'Lon': findlongitude('Kanalweg')},
    {'Locname': 'Haid-und-Neu-Straße', 'Lat': findlatitude('Haid-und-Neu-Straße'), 'Lon': findlongitude('Haid-und-Neu-Straße')},
    {'Locname': 'Blumenstraße', 'Lat': findlatitude('Blumenstraße'), 'Lon': findlongitude('Blumenstraße')},
    {'Locname': 'Gartenstraße', 'Lat': findlatitude('Gartenstraße'), 'Lon': findlongitude('Gartenstraße')},
    {'Locname': 'Bismarckstraße', 'Lat': findlatitude('Bismarckstraße'), 'Lon': findlongitude('Bismarckstraße')},
    {'Locname': 'Kaiserallee', 'Lat': findlatitude('Kaiserallee'), 'Lon': findlongitude('Kaiserallee')},
#    {'Locname': 'Rheinstrandsiedlung', 'Lat': None, 'Lon': None},
    {'Locname': 'Neureuter Hauptstraße', 'Lat': findlatitude('Neureuter%20Hauptstraße'), 'Lon': findlongitude('Neureuter%20Hauptstraße')},
    {'Locname': 'Knielinger Allee', 'Lat': findlatitude('Knielinger%20Allee'), 'Lon': findlongitude('Knielinger%20Allee')},
    {'Locname': 'Grötzinger Straße', 'Lat': findlatitude('Grötzinger%20Straße'), 'Lon': findlongitude('Grötzinger%20Straße')},
    {'Locname': 'Karlsbader Straße', 'Lat': findlatitude('Karlsbader%20Straße'), 'Lon': findlongitude('Karlsbader%20Straße')},
    {'Locname': 'Ettlinger Allee', 'Lat': findlatitude('Ettlinger%20Allee'), 'Lon': findlongitude('Ettlinger%20Allee')},
#    {'Locname': 'Hauptfriedhof', 'Lat': None, 'Lon': None},
#    {'Locname': 'Alter Flugplatz', 'Lat': None, 'Lon': None},    # falsch: Flugpl. (48.984997, 8.332674)
#    {'Locname': 'Schlossgarten', 'Lat': None, 'Lon': None},
#    {'Locname': 'Fasanengarten', 'Lat': None, 'Lon': None},    # falsch: Am Fasanengarten (49.013324, 8.421609)
#    {'Locname': 'Hofgarten', 'Lat': None, 'Lon': None},
#    {'Locname': 'Oberwald', 'Lat': None, 'Lon': None},    # falsch (49.069726, 8.298278)
#    {'Locname': 'Tierpark Oberwald', 'Lat': None, 'Lon': None},    # falsch (49.069726, 8.298278)
#    {'Locname': 'Rheinpark', 'Lat': None, 'Lon': None},
#    {'Locname': 'Citypark', 'Lat': None, 'Lon': None},
    {'Locname': 'Südweststadt', 'Lat': findlatitude('Südweststadt'), 'Lon': findlongitude('Südweststadt')},
    {'Locname': 'Südstadt', 'Lat': findlatitude('Südstadt'), 'Lon': findlongitude('Südstadt')},
    {'Locname': 'Nordstadt', 'Lat': findlatitude('Nordstadt'), 'Lon': findlongitude('Nordstadt')},
    {'Locname': 'Oststadt', 'Lat': findlatitude('Oststadt'), 'Lon': findlongitude('Oststadt')},
    {'Locname': 'Mühlburg', 'Lat': findlatitude('Mühlburg'), 'Lon': findlongitude('Mühlburg')},
    {'Locname': 'Daxlanden', 'Lat': findlatitude('Daxlanden'), 'Lon': findlongitude('Daxlanden')},
    {'Locname': 'Grünwinkel', 'Lat': findlatitude('Grünwinkel'), 'Lon': findlongitude('Grünwinkel')},
    {'Locname': 'Beiertheim-Bulach', 'Lat': findlatitude('Beiertheim-Bulach'), 'Lon': findlongitude('Beiertheim-Bulach')},
    {'Locname': 'Weiherfeld-Dammerstock', 'Lat': findlatitude('Weiherfeld-Dammerstock'), 'Lon': findlongitude('Weiherfeld-Dammerstock')},
    {'Locname': 'Rüppurr', 'Lat': findlatitude('Rüppurr'), 'Lon': findlongitude('Rüppurr')},
    {'Locname': 'Oberreut', 'Lat': findlatitude('Oberreut'), 'Lon': findlongitude('Oberreut')},
    {'Locname': 'Grötzingen', 'Lat': findlatitude('Grötzingen'), 'Lon': findlongitude('Grötzingen')},
    {'Locname': 'Hohenwettersbach', 'Lat': findlatitude('Hohenwettersbach'), 'Lon': findlongitude('Hohenwettersbach')},
    {'Locname': 'Wolfartsweier', 'Lat': findlatitude('Wolfartsweier'), 'Lon': findlongitude('Wolfartsweier')},
    {'Locname': 'Grünwettersbach', 'Lat': findlatitude('Grünwettersbach'), 'Lon': findlongitude('Grünwettersbach')},
    {'Locname': 'Palmbach', 'Lat': findlatitude('Palmbach'), 'Lon': findlongitude('Palmbach')},
    {'Locname': 'Stupferich', 'Lat': findlatitude('Stupferich'), 'Lon': findlongitude('Stupferich')},
    {'Locname': 'Neureut', 'Lat': findlatitude('Neureut'), 'Lon': findlongitude('Neureut')},
    {'Locname': 'Nordweststadt', 'Lat': findlatitude('Nordweststadt'), 'Lon': findlongitude('Nordweststadt')},
    {'Locname': 'Rintheim', 'Lat': findlatitude('Rintheim'), 'Lon': findlongitude('Rintheim')},
    # {'Locname': 'Rheinhafen', 'Lat': findlatitude('Rheinhafen'), 'Lon': findlongitude('Rheinhafen')},
    # {'Locname': 'Alter Schlachthof', 'Lat': findlatitude('Alter%20Schlachthof'), 'Lon': findlongitude('Alter%20Schlachthof')},    # bruh, warum ist das hier alles doppelt drin
    {'Locname': 'Kreativpark Alter Schlachthof', 'Lat': findlatitude('Kreativpark%20Alter%20Schlachthof'), 'Lon': findlongitude('Kreativpark%20Alter%20Schlachthof')},    # siehe Alter Schlachthof
#    {'Locname': 'Filmpalast am ZKM', 'Lat': None, 'Lon': None},
#    {'Locname': 'Europahalle', 'Lat': None, 'Lon': None},
#    {'Locname': 'Stadthalle Karlsruhe', 'Lat': None, 'Lon': None},    # falsch: "Karlsruhe" (49.009716, 8.401216)
#    {'Locname': 'Badisches Staatstheater', 'Lat': None, 'Lon': None},
#    {'Locname': 'Kammertheater Karlsruhe', 'Lat': None, 'Lon': None},    # falsch: "Karlsruhe" (49.009716, 8.401216)
#    {'Locname': 'Sandkorn Theater', 'Lat': None, 'Lon': None},
#    {'Locname': 'Jakobus-Theater', 'Lat': None, 'Lon': None},
#    {'Locname': 'Marotte Figurentheater', 'Lat': None, 'Lon': None},
#    {'Locname': 'Badische Landesbibliothek', 'Lat': None, 'Lon': None},
#    {'Locname': 'Amerikahaus', 'Lat': None, 'Lon': None},
#    {'Locname': 'Bundesverfassungsgericht', 'Lat': None, 'Lon': None},
#    {'Locname': 'Bundesgerichtshof', 'Lat': None, 'Lon': None},
#    {'Locname': 'Generalbundesanwalt', 'Lat': None, 'Lon': None},
#    {'Locname': 'Landesbibliothek', 'Lat': None, 'Lon': None},
#    {'Locname': 'Ständehaus', 'Lat': None, 'Lon': None},
#    {'Locname': 'Prinz-Max-Palais', 'Lat': None, 'Lon': None},    # falsch (48.996984, 8.53466)
#    {'Locname': 'Stadtmuseum Karlsruhe', 'Lat': None, 'Lon': None},    # falsch: "Karlsruhe" (49.009716, 8.401216)
#    {'Locname': 'Pyramide am Marktplatz', 'Lat': None, 'Lon': None},    # falsch (48.999157, 8.471262)
#    {'Locname': 'Evangelische Stadtkirche', 'Lat': None, 'Lon': None},
#    {'Locname': 'St. Stephan Kirche', 'Lat': None, 'Lon': None},    # nicht None wenn ohne ?autocomplete=false, dann "Kirchstr." in Karlsruhe (trotzdem falsch)
#    {'Locname': 'Kleine Kirche', 'Lat': None, 'Lon': None},
#    {'Locname': 'Christuskirche', 'Lat': None, 'Lon': None},
#    {'Locname': 'St. Bernhard Kirche', 'Lat': None, 'Lon': None},
#    {'Locname': 'St. Elisabeth Kirche', 'Lat': None, 'Lon': None},
#    {'Locname': 'St. Konrad Kirche', 'Lat': None, 'Lon': None},
    {'Locname': 'St. Peter und Paul Kirche', 'Lat': findlatitude('St.%20Peter%20und%20Paul%20Kirche'), 'Lon': findlongitude('St.%20Peter%20und%20Paul%20Kirche')},
#    {'Locname': 'St. Michael Kirche', 'Lat': None, 'Lon': None}
]

# ZUM KOORDINATEN PRÜFEN
# for location in locations:
#    print(location['Locname'], location['Lat'], location['Lon'])

print("Ermittle Stadtteile der Locations...")

# Konvertieren in GeoDataFrame zum Shapefile-Abgleich der Koordinaten
unserdf = pd.DataFrame(locations)    # Konversion in (Geo-)Pandas-DataFrame zur weiteren Arbeit mit GeoPandas
unsergdf = gpd.GeoDataFrame(unserdf, geometry=[Point(laenge, breite) for laenge, breite in zip(unserdf['Lon'], unserdf['Lat'])], crs='EPSG:4326').to_crs(epsg=25832)    # Umwandlung der Koordinaten unserer Locations ins UTM-System der Shapefile-Datei der Stadt KA
kashapefilegdf = gpd.read_file("Stadtteile_Karlsruhe.shp")    # Einlesen der Shapefile-Datei der Stadt Karlsruhe mit den Stadtteilgrenzen
# print(unsergdf.head())    # debug
# print(kashapefilegdf.head())    # debug
joinedgdf = gpd.sjoin(unsergdf, kashapefilegdf, how='left', predicate='within')    # eigentlicher Abgleich
# print(joinedgdf.head())    # debug

# Stadtteil herausfinden
def finddistrict(place):
    for _, row in joinedgdf.iterrows():    # 2D, da sonst durch Spalten statt Zeilen iteriert wird
        if row['Locname'] == place:
            return row['NAME']    # NAME = Name der Stadtteil-Spalte in der Shapefile-Datei der Stadt KA
    return None


purposes = ['Arbeit', 'Einkaufen', 'Freizeit', 'Schule/Uni', 'Begleitung', 'Erholung', 'Sport', 'Arztbesuch']
modes = ['Auto', 'Fahrrad', 'ÖPNV', 'zu Fuß', 'E-Scooter', 'multimodal']

# Dauer nach Zweck
def purpose_duration(purpose):
    if purpose in ['Arbeit', 'Schule/Uni']:
        return random.randint(240, 540)
    elif purpose in ['Einkaufen', 'Arztbesuch']:
        return random.randint(30, 90)
    elif purpose in ['Freizeit', 'Sport', 'Erholung']:
        return random.randint(60, 180)
    elif purpose == 'Begleitung':
        return random.randint(10, 30)
    else:
        return random.randint(30, 120)

# Distanzschätzung    # TODO: tatsächlich berechnen lassen
def estimate_distance(loc1, loc2):    # Funktion umbenennen
    base = random.uniform(0.5, 2.0)
    if loc1 == loc2:
        return round(base, 1)    # math.dist((loc1.lat, loc1.lon), (loc2.lat, loc2.lon)) oder Ähnlich
    return round(base + random.uniform(1.5, 6.0), 1)    # return distance stattdessen

# Ergebnisse sammeln
rows = []

print("Generiere Wegetagebuch...")

# Erstellung des Wegetagebuchs
for person_id in range(1, num_people + 1):
    age = ages[person_id - 1]
    gender = genders[person_id - 1]
    occupation = random.choice(occupations)
    household = random.choice(households)
    district = random.choice(districts)

    num_trips = random.randint(min_trips_per_person, max_trips_per_person)
    trip_locations = random.sample(locations, k=num_trips + 1)
    current_time = datetime.strptime("05:30", "%H:%M") + timedelta(minutes=random.randint(0, 90))

    person_trips = []

    for trip_index in range(num_trips):
        start_time = current_time
        travel_duration = timedelta(minutes=random.randint(10, 45))
        end_time = start_time + travel_duration
        activity_duration = timedelta(minutes=purpose_duration(random.choice(purposes)))
        current_time = end_time + activity_duration

        start_location = trip_locations[trip_index]["Locname"]
        end_location = trip_locations[trip_index + 1]["Locname"]
        # start_coordinatelat = trip_locations[trip_index]["Lat"]
        # start_coordinatelon = trip_locations[trip_index]["Lon"]
        # end_coordinatelat = trip_locations[trip_index + 1]["Lat"]
        # end_coordinatelon = trip_locations[trip_index + 1]["Lon"]
        start_district = finddistrict(start_location)    # für ergänzte Spalten zur CSV-Auswertung in wegetagebuchauswerter.py
        end_district = finddistrict(end_location)    # s.o.
        purpose = random.choice(purposes)
        mode = random.choice(modes)
        distance = estimate_distance(start_location, end_location)
        multimodal = 'ja' if mode == 'multimodal' else 'nein'

        person_trips.append({
            'PersonenID': person_id,
            'Alter': age,
            'Geschlecht': gender,
            'Beruf': occupation,
            'Haushaltstyp': household,
            'Wohnviertel': district,
            'Startzeit': start_time.strftime('%H:%M'),
            'Endzeit': end_time.strftime('%H:%M'),
            'Startort': start_location,
            'Zielort': end_location,
            'Zweck': purpose,
            'Entfernung_km': distance,
            'Verkehrsmittel': mode,
            'Multimodal': multimodal,
            # 'Startortbreitengrad': start_coordinatelat,
            # 'Startortlangengrad': start_coordinatelon,
            # 'Zielortbreitengrad': end_coordinatelat,
            # 'Zielortlangengrad': end_coordinatelon,
            'Startviertel': start_district,    # ergänzte Spalten
            'Zielviertel': end_district    # s.o.
        })

    # Heimweg hinzufügen
    if person_trips[-1]['Zielort'] != person_trips[0]['Startort']:
        start_location = person_trips[-1]['Zielort']
        end_location = person_trips[0]['Startort']
        # start_coordinatelat = trip_locations[trip_index]["Lat"]
        # start_coordinatelon = trip_locations[trip_index]["Lon"]
        # end_coordinatelat = trip_locations[trip_index + 1]["Lat"]
        # end_coordinatelon = trip_locations[trip_index + 1]["Lon"]
        start_district = finddistrict(start_location)    # s.o.
        end_district = finddistrict(end_location)    # s.o.
        travel_duration = timedelta(minutes=random.randint(10, 45))
        start_time = current_time
        end_time = start_time + travel_duration
        mode = random.choice(modes)
        multimodal = 'ja' if mode == 'multimodal' else 'nein'
        distance = estimate_distance(start_location, end_location)

        person_trips.append({
            'PersonenID': person_id,
            'Alter': age,
            'Geschlecht': gender,
            'Beruf': occupation,
            'Haushaltstyp': household,
            'Wohnviertel': district,
            'Startzeit': start_time.strftime('%H:%M'),
            'Endzeit': end_time.strftime('%H:%M'),
            'Startort': start_location,
            'Zielort': end_location,
            'Zweck': 'Heimweg',
            'Entfernung_km': distance,
            'Verkehrsmittel': mode,
            'Multimodal': multimodal,
            # 'Startortbreitengrad': start_coordinatelat,
            # 'Startortlangengrad': start_coordinatelon,
            # 'Zielortbreitengrad': end_coordinatelat,
            # 'Zielortlangengrad': end_coordinatelon,
            'Startviertel': start_district,    # ergänzte Spalten
            'Zielviertel': end_district    # s.o.
        })

    rows.extend(person_trips)

print("Exportiere Wegetagebuch...")

# Als DataFrame
df_final = pd.DataFrame(rows)
csv_path = r"wegetagebuch_karlsruhe.csv"    # r-String anscheinend um Backslashes und so (normalerweise Backspace) zu ignorieren
df_final.to_csv(csv_path, index=False)

print("Fertig")

# Anzeigen des Shapefiles zum Erfahren aller möglichen Stadtteilnamen
# print(kashapefilegdf)    # debug