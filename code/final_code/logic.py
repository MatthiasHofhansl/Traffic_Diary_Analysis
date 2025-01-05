# This module handles data processing, CSV operations and geocoding logic.

import os
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import MapBox
from datetime import datetime

# global constants
DATA_FILE = "traffic_diary.csv"
USER_FILE = "users.csv"
CHART_DIRECTORY = "charts"

MAPBOX_API_KEY = (
    "pk.eyJ1IjoibWF0dGhpYXNoZmwiLCJhIjoiY201ZWI5dzBkMjU2MjJ1czc2ZTI0OTlnNyJ9."
    "6DFtWqtEQp5ufQeodVZ5dQ"
)

# Create a global Geolocator-Objekt
geolocator = MapBox(api_key=MAPBOX_API_KEY)


# ------------------ Allgemeine Helper-Funktionen ------------------
def handle_error(msg, label):
    """Zeigt eine Fehlermeldung im GUI (roter Text) an."""
    label.config(text=msg, foreground="red")


def show_success(msg, label):
    """Zeigt eine Erfolgsnachricht im GUI (grüner Text) an."""
    label.config(text=msg, foreground="green")


def create_chart_directory():
    """Erzeugt den Ordner für Diagramme, falls er nicht existiert."""
    if not os.path.exists(CHART_DIRECTORY):
        os.makedirs(CHART_DIRECTORY)


def parse_or_reverse_geocode(s):
    """
    Bestimmt Koordinaten zu einem Adress- oder Koordinatentext.
    - Ist 's' eine Koordinate (lat, lon), wird per Reverse-Geocoding validiert.
    - Ist 's' eine Adresse, wird per Forward-Geocoding die Koordinate gesucht.
    Gibt ein Tupel (lat, lon) oder None zurück.
    """
    if "," in s:
        try:
            lat_str, lon_str = s.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            location = geolocator.reverse((lat, lon))
            return (lat, lon) if location else None
        except ValueError:
            pass
    loc = geolocator.geocode(s)
    return (loc.latitude, loc.longitude) if loc else None


def calculate_distance(start_point, end_point):
    """Berechnet die Distanz (in km) zwischen zwei Adressen/Koordinaten."""
    try:
        start_coords = parse_or_reverse_geocode(start_point)
        end_coords = parse_or_reverse_geocode(end_point)
        if not start_coords or not end_coords:
            return None
        return geodesic(start_coords, end_coords).kilometers
    except:
        return None


def save_to_csv(data, file_name):
    """
    Hängt einen Dictionary-Eintrag (Zeile) an eine CSV-Datei an.
    Existiert sie nicht, wird sie neu erstellt.
    """
    df = pd.DataFrame([data])
    if not os.path.exists(file_name):
        df.to_csv(file_name, index=False)
    else:
        df.to_csv(file_name, mode="a", header=False, index=False)


def load_csv(file_name):
    """
    Lädt eine CSV-Datei als pandas DataFrame.
    Existiert sie nicht, wird None zurückgegeben.
    """
    if not os.path.exists(file_name):
        return None
    return pd.read_csv(file_name)