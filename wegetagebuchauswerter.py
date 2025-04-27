# Programmieren (HKA Verkehrssystemmanagement), SS 2025
# Gruppe: Arsalan, Ilja, Janusz, Ufuk
# Projekt: TODO NAME (Code 2/2)

import csv
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
import holoviews as hv    # "pip install holoviews" ausführen (ohne "")
import folium
from folium.plugins import HeatMap, HeatMapWithTime
from bokeh.plotting import show    # siehe unten
from holoviews import opts

# Koordinaten finden (Mapbox-API-Abfrage, gleicher Code wie beim Wegetagebuch-Generator)
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

# MAIN
def main():  
    # Zähle Wege im Wegetagebuch nach Start- und Zielviertel
    print("Zähle Wege im Wegetagebuch nach Start- und Zielviertel...")
    wegetagebuchdf = pd.read_csv("wegetagebuch_karlsruhe.csv")

    count_combinations = wegetagebuchdf.groupby(['Startviertel', 'Zielviertel']).size().reset_index(name='Value').sort_values(by='Value', ascending=False).head(40)    # .groupby() + .size() für Vorkommen von Kombinationen (2D), reset_index() für DataFrame als Return

    # jetzt nochmal getrennt für die Heatmap...
    dfzusammen = pd.concat([wegetagebuchdf['Startviertel'], wegetagebuchdf['Zielviertel']])
    count_viertelwege = dfzusammen.value_counts().reset_index(name='Wegeanzahl')
    count_viertelwege['Lat'] = count_viertelwege['index'].apply(findlatitude)    # keine Schleife/Argument benötigt, Pandas-apply macht das automatisch
    count_viertelwege['Lon'] = count_viertelwege['index'].apply(findlongitude)
    count_viertelwege.drop(columns=['index'], inplace=True)    # Entfernen von unbrauchbaren Spalten für Folium
    count_viertelwege = count_viertelwege[['Lat', 'Lon', 'Wegeanzahl']]    # Sortieren der Spalten für Folium
    # print(count_viertelwege)    # debug
    
    print("Zähle Wege im Wegetagebuch nach anderen Kriterien...")
    # Zähle Wege im Wegetagebuch nach Verkehrsmittel (Gruppierung, Verkehrsmittelmix für Bericht + Ergebnisgrafik=ModalSplit)
    count_verkehrsmittel = wegetagebuchdf['Verkehrsmittel'].value_counts().reset_index(name='Wegeanzahl')    # value_counts (wie in Pandas-Dokumentation) bei 1D
    # print(count_verkehrsmittel)    # debug

    # Zähle zurückgelegte Wege nach Beruf (für Bericht)
    count_beruf = wegetagebuchdf['Beruf'].value_counts().reset_index(name='Wegeanzahl')
    # Zähle Wege nach ZWECK (Gruppierung, für Ergebnisgrafik), der Vollständigkeit halber, wahrscheinlich wenig überraschend
    count_zweck = wegetagebuchdf['Zweck'].value_counts().reset_index(name='Wegeanzahl')

    # Zähle Wege nach Zielviertel (für Bericht/Analyse)
    count_zielviertel = wegetagebuchdf['Zielviertel'].value_counts().reset_index(name='Wegeanzahl')

    # punkte auf stadtteilen mit verschiedenen farben je nachdem wie oft als start- ODER zielort auf foliumkarte ergänzen (heatmap da pfeile nur wichtigste relationen zeigen)
    # entfernung fixen (math.dist)

    # print(count_combinations)    # debug

    # Erzeuge Chord-Diagramm
    print("Erzeuge Chord-Diagramm...")
    hv.extension("bokeh")    # Wähle Bokeh als Renderer
    hv.output(size=320)
    count_combinations = count_combinations.rename(columns={'Startviertel': 'Source', 'Zielviertel': 'Target'})    # Umbenennen der Spalten ins Holoviews-Format (Source, Target, Value)

    viertel = hv.Dataset(pd.DataFrame({'Source': count_combinations['Source'].unique(), 'index': range(len(count_combinations['Source'].unique()))}), 'Source')    # für Labels beim Diagramm
    chorddiagramm = hv.Chord((count_combinations, viertel)).opts(opts.Chord(cmap='TolRainbow', edge_cmap='TolRainbow', node_color = hv.dim('index'), edge_color = hv.dim('Source').str(), labels='Source'))    # Erzeuge Chord-Diagramm
    # https://stackoverflow.com/questions/65297178/holoviews-chord-diagram-how-to-get-edges-nodes-to-have-the-same-color
    # dazu: .select(___, None) bringt nichts, stattdessen .head(___) oben

    # Karte erstellen
    # https://medium.com/@vinodvidhole/interesting-heatmaps-using-python-folium-ee41b118a996
    print("Erstelle Karte...")
    karte = folium.Map(location = [49.0140, 8.4043], zoom_start=12, tiles = "Cartodb Positron")    # Koordinaten: Karlsruhe Zentrum, andere tiles für höheren Kontrast
    HeatMap(count_viertelwege, min_opacity=0.50, blur=25).add_to(karte)

    for _, row in count_combinations.iterrows():    # auch wenn nach Zeile/row iteriert wird, braucht es 2 Dinger weil das DataFrame tabellenförmig ist
        folium.PolyLine(locations = [(findlatitude(row['Source']), findlongitude(row['Source'])), (findlatitude(row['Target']), findlongitude(row['Target']))], weight = row['Value'] / 20).add_to(karte)

    karte.save('Karte.html')
    print("Karte im Ordner des Codes generiert!")

    # Öffne Chord-Diagramm
    print("Öffne Chord-Diagramm...")
    show(hv.render(chorddiagramm))    # Befehl nötig damit HTML gespeichert und (bei VS Code) geöffnet wird

    # Exportiere wichtigste Relationen als Tabelle (für Abgabe, Präsentation usw.)
    print("Exportiere CSV-Dateien für Tabellen...")
    count_combinations = count_combinations.rename(columns={'Source': 'Startviertel', 'Target': 'Zielviertel', 'Value': 'Wegeanzahl'})
    count_combinations.to_csv("wichtigste_relationen.csv", index=False)    # index=False für keine Extraspalte mit Zeilennummer
    count_verkehrsmittel.to_csv("modal_split.csv", index=False)
    count_beruf.to_csv("beruf_split.csv", index=False)
    count_zweck.to_csv("zweck_split.csv", index=False)
    count_zielviertel.to_csv("zielviertel_split.csv", index=False)
    print("Fertig!")

# Main ausführen!
if __name__ == "__main__":
    main()