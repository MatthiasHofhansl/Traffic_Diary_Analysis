import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import MapBox
from datetime import datetime

# NEUE IMPORTS für Diagramme und erweiterte Analysen
import matplotlib.pyplot as plt
import seaborn as sns

# NEUER IMPORT, um PNG-Dateien in Tkinter anzuzeigen
from PIL import Image, ImageTk

DATA_FILE = "traffic_diary.csv"
USER_FILE = "users.csv"
MAPBOX_API_KEY = "pk.eyJ1IjoibWF0dGhpYXNoZmwiLCJhIjoiY201ZWI5dzBkMjU2MjJ1czc2ZTI0OTlnNyJ9.6DFtWqtEQp5ufQeodVZ5dQ"
CHART_DIRECTORY = "charts"

geolocator = MapBox(api_key=MAPBOX_API_KEY)

def handle_error(msg, label):
   """Zeigt eine Fehlermeldung im GUI an."""
   label.config(text=msg, foreground="red")

def show_success(msg, label):
   """Zeigt eine Erfolgsnachricht im GUI an."""
   label.config(text=msg, foreground="green")

def create_chart_directory():
   """Erzeugt den Ordner für Diagramme, wenn er nicht existiert."""
   if not os.path.exists(CHART_DIRECTORY):
       os.makedirs(CHART_DIRECTORY)

def calculate_distance(start_point, end_point):
   """
   Berechnet die Distanz (in km) zwischen zwei Adressen (start_point, end_point)
   mithilfe von geopy und MapBox.
   """
   try:
       start_coords = geolocator.geocode(start_point)
       end_coords = geolocator.geocode(end_point)
       if not start_coords or not end_coords:
           return None
       return geodesic(
           (start_coords.latitude, start_coords.longitude),
           (end_coords.latitude, end_coords.longitude)
       ).kilometers
   except:
       return None

def save_to_csv(data, file_name):
   """
   Speichert einen Dictionary-Eintrag als neue Zeile in einer CSV-Datei.
   Existiert die Datei nicht, wird sie neu erstellt; sonst wird die Zeile angehängt.
   """
   df = pd.DataFrame([data])
   if not os.path.exists(file_name):
       df.to_csv(file_name, index=False)
   else:
       df.to_csv(file_name, mode="a", header=False, index=False)

def load_csv(file_name):
   """
   Lädt eine CSV-Datei als pandas DataFrame und gibt sie zurück.
   Existiert die Datei nicht, wird None zurückgegeben.
   """
   if not os.path.exists(file_name):
       return None
   return pd.read_csv(file_name)

class TrafficDiaryApp:
   """
   Haupt-Klasse für die Tkinter-Anwendung.
   Enthält alle GUI-Elemente und die zugehörige Logik.
   """
   def __init__(self, root):
       self.root = root
       self.root.title("Traffic Diary Analysis Tool")

       # -----------------------------------
       #  Zeile 0: Benutzer-Auswahl
       # -----------------------------------
       ttk.Label(root, text="Benutzer/in:").grid(row=0, column=0, padx=5, pady=5)
       self.user_var = tk.StringVar()
       self.user_menu = ttk.Combobox(root, textvariable=self.user_var, state="readonly")
       self.user_menu.grid(row=0, column=1, padx=5, pady=5)

       # Benutzer in die Combobox laden
       self.load_users()

       # Button zum Hinzufügen neuer Benutzer
       ttk.Button(root, text="Neue/n Benutzer/in anlegen", command=self.add_new_user).grid(
           row=0, column=2, padx=5, pady=5
       )

       # -----------------------------------
       #  NEU: Zeile 1: Startdatum
       # -----------------------------------
       ttk.Label(root, text="Startdatum:").grid(row=1, column=0, padx=5, pady=5)
       self.start_date_var = tk.StringVar()
       self.start_date_btn = ttk.Button(root, text="Startdatum wählen", command=self.select_start_date)
       self.start_date_btn.grid(row=1, column=1, padx=5, pady=5)
       self.start_date_label = ttk.Label(root, textvariable=self.start_date_var)
       self.start_date_label.grid(row=1, column=2, padx=5, pady=5)

       # -----------------------------------
       #  NEU: Zeile 2: Enddatum
       # -----------------------------------
       ttk.Label(root, text="Enddatum:").grid(row=2, column=0, padx=5, pady=5)
       self.end_date_var = tk.StringVar()
       self.end_date_btn = ttk.Button(root, text="Enddatum wählen", command=self.select_end_date)
       self.end_date_btn.grid(row=2, column=1, padx=5, pady=5)
       self.end_date_label = ttk.Label(root, textvariable=self.end_date_var)
       self.end_date_label.grid(row=2, column=2, padx=5, pady=5)

       # -----------------------------------
       #  ANPASSUNG: Zeile 3: Startzeit
       # -----------------------------------
       ttk.Label(root, text="Startzeit:").grid(row=3, column=0, padx=5, pady=5)
       self.start_time_var = tk.StringVar()
       self.start_time_btn = ttk.Button(root, text="Startzeit wählen", command=self.select_start_time)
       self.start_time_btn.grid(row=3, column=1, padx=5, pady=5)
       self.start_time_label = ttk.Label(root, textvariable=self.start_time_var)
       self.start_time_label.grid(row=3, column=2, padx=5, pady=5)

       # -----------------------------------
       #  ANPASSUNG: Zeile 4: Endzeit
       # -----------------------------------
       ttk.Label(root, text="Endzeit:").grid(row=4, column=0, padx=5, pady=5)
       self.end_time_var = tk.StringVar()
       self.end_time_btn = ttk.Button(root, text="Endzeit wählen", command=self.select_end_time)
       self.end_time_btn.grid(row=4, column=1, padx=5, pady=5)
       self.end_time_label = ttk.Label(root, textvariable=self.end_time_var)
       self.end_time_label.grid(row=4, column=2, padx=5, pady=5)

       # -----------------------------------
       #  (Unverändert) Zeile 5: Startpunkt
       # -----------------------------------
       ttk.Label(root, text="Startpunkt:").grid(row=5, column=0, padx=5, pady=5)
       self.start_point_var = tk.StringVar()
       self.start_point_entry = ttk.Entry(root, textvariable=self.start_point_var)
       self.start_point_entry.grid(row=5, column=1, padx=5, pady=5)

       # -----------------------------------
       #  (Unverändert) Zeile 6: Endpunkt
       # -----------------------------------
       ttk.Label(root, text="Endpunkt:").grid(row=6, column=0, padx=5, pady=5)
       self.end_point_var = tk.StringVar()
       self.end_point_entry = ttk.Entry(root, textvariable=self.end_point_var)
       self.end_point_entry.grid(row=6, column=1, padx=5, pady=5)

       # -----------------------------------
       #  (Unverändert) Zeile 7: Verkehrsmittel
       # -----------------------------------
       ttk.Label(root, text="Verkehrsmittel:").grid(row=7, column=0, padx=5, pady=5)
       self.mode_var = tk.StringVar(value="")
       mode_list = ["Fahrrad", "Fuß", "MIV", "MIV-Mitfahrer", "Sonstiges", "ÖV"]
       mode_list_sorted = sorted(mode_list, key=str.lower)
       self.mode_box = ttk.Combobox(
           root,
           textvariable=self.mode_var,
           values=mode_list_sorted,
           state="readonly"
       )
       self.mode_box.grid(row=7, column=1, padx=5, pady=5)

       # -----------------------------------
       #  (Unverändert) Zeile 8: Wegezweck
       # -----------------------------------
       ttk.Label(root, text="Wegezweck:").grid(row=8, column=0, padx=5, pady=5)
       self.purpose_var = tk.StringVar(value="")
       purpose_list = ["Arbeit", "Dienstlich", "Ausbildung", "Einkauf", "Erledigung", "Freizeit", "Begleitung"]
       purpose_list_sorted = sorted(purpose_list, key=str.lower)
       self.purpose_box = ttk.Combobox(
           root,
           textvariable=self.purpose_var,
           values=purpose_list_sorted,
           state="readonly"
       )
       self.purpose_box.grid(row=8, column=1, padx=5, pady=5)

       # -----------------------------------
       #  (Unverändert) Zeile 9: Speichern-Button
       # -----------------------------------
       ttk.Button(root, text="Speichern", command=self.save_entry).grid(
           row=9, column=0, columnspan=2, padx=5, pady=10
       )

       # -----------------------------------
       #  (Unverändert) Zeile 10: Auswerten-Button
       # -----------------------------------
       ttk.Button(root, text="Jetzt auswerten", command=self.analyze_data).grid(
           row=10, column=0, columnspan=2, padx=5, pady=10
       )

       # -----------------------------------
       #  (Unverändert) Zeile 11: Zurücksetzen-Button
       # -----------------------------------
       ttk.Button(root, text="Zurücksetzen", command=self.reset_all).grid(
           row=11, column=0, columnspan=2, padx=5, pady=10
       )

       # -----------------------------------
       #  (Unverändert) Zeile 12: Meldungs-Label
       # -----------------------------------
       self.message_label = ttk.Label(root, text="")
       self.message_label.grid(row=12, column=0, columnspan=3, padx=5, pady=5)

       # Bei Änderung in den Eingabe-Feldern wird die Meldung gelöscht
       self.start_point_var.trace_add("write", self.clear_message)
       self.end_point_var.trace_add("write", self.clear_message)
       self.mode_var.trace_add("write", self.clear_message)
       self.user_var.trace_add("write", self.clear_message)
       self.start_time_var.trace_add("write", self.clear_message)
       self.end_time_var.trace_add("write", self.clear_message)
       self.purpose_var.trace_add("write", self.clear_message)
       self.start_date_var.trace_add("write", self.clear_message)
       self.end_date_var.trace_add("write", self.clear_message)

   # --------------------------------------------------
   # Lese- und Schreibfunktionen für Benutzer
   # --------------------------------------------------
   def load_users(self):
       """Lädt die Benutzer aus der CSV-Datei und befüllt das Dropdown-Menü."""
       self.user_menu['values'] = []
       if os.path.exists(USER_FILE):
           users = pd.read_csv(USER_FILE)
           user_list = sorted(users["Vorname"] + " " + users["Nachname"])
           self.user_menu['values'] = user_list

   def add_new_user(self):
       """Öffnet ein neues Fenster, um einen neuen Benutzer anzulegen."""
       def save_user(event=None):
           first_name = first_name_var.get().strip()
           last_name = last_name_var.get().strip()
           if not first_name or not last_name:
               handle_error("Bitte Vor- und Nachname angeben.", message_label)
               return

           user_full_name = f"{first_name} {last_name}"
           user_full_name_lower = user_full_name.lower()

           if os.path.exists(USER_FILE):
               existing_users = pd.read_csv(USER_FILE)
               existing_full_names_lower = (
                   existing_users["Vorname"].str.lower() + " " + existing_users["Nachname"].str.lower()
               )
               if user_full_name_lower in existing_full_names_lower.values:
                   handle_error("Benutzer/in bereits vorhanden.", message_label)
                   return

           new_user = pd.DataFrame([{"Vorname": first_name, "Nachname": last_name}])
           if not os.path.exists(USER_FILE):
               new_user.to_csv(USER_FILE, index=False)
           else:
               existing_users = pd.read_csv(USER_FILE)
               updated_users = pd.concat([existing_users, new_user], ignore_index=True)
               updated_users.to_csv(USER_FILE, index=False)

           self.load_users()
           self.user_var.set(user_full_name)
           user_window.destroy()

       user_window = tk.Toplevel(self.root)
       user_window.title("Neue/n Benutzer/in anlegen")

       ttk.Label(user_window, text="Vorname:").grid(row=0, column=0, padx=5, pady=5)
       first_name_var = tk.StringVar()
       first_name_entry = ttk.Entry(user_window, textvariable=first_name_var)
       first_name_entry.grid(row=0, column=1, padx=5, pady=5)

       ttk.Label(user_window, text="Nachname:").grid(row=1, column=0, padx=5, pady=5)
       last_name_var = tk.StringVar()
       last_name_entry = ttk.Entry(user_window, textvariable=last_name_var)
       last_name_entry.grid(row=1, column=1, padx=5, pady=5)

       message_label = ttk.Label(user_window, text="")
       message_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

       save_button = ttk.Button(user_window, text="Speichern", command=save_user)
       save_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

       # Fokus direkt auf das erste Eingabefeld setzen (optional)
       first_name_entry.focus()

       # Enter-Taste an save_user binden
       user_window.bind("<Return>", save_user)

   # --------------------------------------------------
   # NEUE METHODEN: Datum wählen (Kalender)
   #    -> Datum automatisch übernehmen (ohne OK)
   #    -> Format: dd.mm.yyyy
   # --------------------------------------------------
   def select_start_date(self):
       """Öffnet ein Kalender-Widget, um das Startdatum auszuwählen."""
       self.select_date(self.start_date_var, "Startdatum")

   def select_end_date(self):
       """Öffnet ein Kalender-Widget, um das Enddatum auszuwählen."""
       self.select_date(self.end_date_var, "Enddatum")

   def select_date(self, variable, title):
       """Allgemeine Funktion, um über Kalender ein Datum auszuwählen."""
       top = tk.Toplevel(self.root)
       top.title(title)

       # tkcalendar mit gewünschtem Format: dd.mm.yyyy
       cal = Calendar(top, selectmode="day", date_pattern="dd.mm.yyyy")
       cal.pack(pady=10)

       # Sobald ein Datum angeklickt wird, soll es automatisch übernommen werden
       def on_date_selected(event):
           date = cal.get_date()  # Das Datum ist bereits im Format dd.mm.yyyy
           variable.set(date)
           top.destroy()

       # Event binden, das bei Auswahl eines Datums getriggert wird
       cal.bind("<<CalendarSelected>>", on_date_selected)

   # --------------------------------------------------
   # NEUE METHODEN: Uhrzeit wählen mit Doppelpunkt
   #   und nur 2 Ziffern pro Feld,
   #   Bestätigung per Enter (kein Extra-OK)
   # --------------------------------------------------
   def select_start_time(self):
       """Öffnet ein Fenster, um die Startzeit (Stunde und Minute) einzugeben."""
       self.select_time(self.start_time_var, "Startzeit")

   def select_end_time(self):
       """Öffnet ein Fenster, um die Endzeit (Stunde und Minute) einzugeben."""
       self.select_time(self.end_time_var, "Endzeit")

   def select_time(self, variable, title):
       """
       Öffnet ein kleines Fenster mit Entry-Feldern für Stunde und Minute,
       getrennt durch einen Doppelpunkt.
       Nur zwei Ziffern werden akzeptiert, bestätigt wird per Enter.
       """

       top = tk.Toplevel(self.root)
       top.title(title)

       time_frame = ttk.Frame(top)
       time_frame.pack(padx=10, pady=10)

       # --- ALT: Spinboxes (auskommentiert, NICHT gelöscht) ---
       #
       # def save_time():
       #     hour = hour_var.get()
       #     minute = minute_var.get()
       #     time_str = f"{hour:02d}:{minute:02d}"
       #     variable.set(time_str)
       #     top.destroy()
       #
       # hour_var = tk.IntVar(value=0)
       # minute_var = tk.IntVar(value=0)
       #
       # ttk.Label(time_frame, text="Stunde:").grid(row=0, column=0, padx=5, pady=5)
       # hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=3)
       # hour_spinbox.grid(row=0, column=1, padx=5, pady=5)
       #
       # ttk.Label(time_frame, text="Minute:").grid(row=1, column=0, padx=5, pady=5)
       # minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=3)
       # minute_spinbox.grid(row=1, column=1, padx=5, pady=5)
       #
       # ttk.Button(top, text="OK", command=save_time).pack(pady=10)

       # --- NEU: Zwei Eingabefelder mit Doppelpunkt ---
       ttk.Label(time_frame, text="Stunde (00-23):").grid(row=0, column=0, padx=5, pady=5)
       hour_var = tk.StringVar()
       hour_entry = ttk.Entry(time_frame, textvariable=hour_var, width=2)
       hour_entry.grid(row=0, column=1, padx=2, pady=5)

       ttk.Label(time_frame, text=":").grid(row=0, column=2, padx=2, pady=5)

       ttk.Label(time_frame, text="Minute (00-59):").grid(row=0, column=3, padx=5, pady=5)
       minute_var = tk.StringVar()
       minute_entry = ttk.Entry(time_frame, textvariable=minute_var, width=2)
       minute_entry.grid(row=0, column=4, padx=2, pady=5)

       # Gemeinsame Funktion zum Validieren und Setzen
       def confirm_time(event=None):
           h = hour_var.get()
           m = minute_var.get()

           # Prüfung auf genau 2 Ziffern
           if len(h) != 2 or len(m) != 2:
               handle_error("Bitte exakt 2 Ziffern für Stunde und Minute eingeben.", self.message_label)
               return
           if not (h.isdigit() and m.isdigit()):
               handle_error("Nur Ziffern sind erlaubt (z.B. 07:05).", self.message_label)
               return

           hour_int = int(h)
           minute_int = int(m)
           if not (0 <= hour_int <= 23):
               handle_error("Stunde muss zwischen 00 und 23 liegen.", self.message_label)
               return
           if not (0 <= minute_int <= 59):
               handle_error("Minute muss zwischen 00 und 59 liegen.", self.message_label)
               return

           # Alles gut, Zeit übernehmen
           time_str = f"{h}:{m}"
           variable.set(time_str)
           top.destroy()

       # Enter-Taste löst confirm_time aus
       top.bind("<Return>", confirm_time)

       # Fokus direkt auf die Stunde setzen
       hour_entry.focus()

   # --------------------------------------------------
   # Speichern und Validierung
   # --------------------------------------------------
   def save_entry(self):
       """
       Speichert einen neuen Tagebucheintrag für Fahrten.
       Überprüft, ob alle Felder ausgefüllt sind und berechnet die Distanz über Geopy.
       """
       user = self.user_var.get()
       start_date = self.start_date_var.get()
       end_date = self.end_date_var.get()
       start_time = self.start_time_var.get()
       end_time = self.end_time_var.get()
       start_point = self.start_point_var.get()
       end_point = self.end_point_var.get()
       mode = self.mode_var.get()
       purpose = self.purpose_var.get()

       if not all([user, start_date, start_time, end_date, end_time, start_point, end_point, mode, purpose]):
           handle_error("Bitte alle Felder ausfüllen.", self.message_label)
           return

       # Du hast nun das Datum im Format "dd.mm.yyyy"
       # Für spätere Auswertungen könnte ein "YYYY-MM-DD"-Format sinnvoll sein.
       # Hier allerdings speichern wir es direkt als String in die CSV.
       start_datetime_str = f"{start_date} {start_time}"
       end_datetime_str = f"{end_date} {end_time}"

       dist = calculate_distance(start_point, end_point)
       if dist is None:
           handle_error("Distanz konnte nicht berechnet werden.", self.message_label)
           return

       entry = {
           "Benutzer/in": user,
           "Startdatum": start_date,
           "Startzeit": start_time,
           "Enddatum": end_date,
           "Endzeit": end_time,
           "Startzeit_kombiniert": start_datetime_str,  # optional für spätere Auswertung
           "Endzeit_kombiniert": end_datetime_str,      # optional für spätere Auswertung
           "Startpunkt": start_point,
           "Endpunkt": end_point,
           "Distanz (km)": dist,
           "Modus": mode,
           "Wegezweck": purpose,
       }
       save_to_csv(entry, DATA_FILE)

       show_success("Der Eintrag wurde erfolgreich abgespeichert.", self.message_label)
       self.clear_fields()

   def clear_fields(self):
       """Setzt die Eingabefelder zurück (außer Benutzer, falls gewünscht)."""
       self.user_menu.set("")
       self.start_date_var.set("")
       self.end_date_var.set("")
       self.start_time_var.set("")
       self.end_time_var.set("")
       self.start_point_var.set("")
       self.end_point_var.set("")
       self.mode_var.set("")
       self.purpose_var.set("")

   def clear_message(self, *args):
       """Löscht die Status-Nachricht in der GUI, sobald etwas Neues eingegeben wird."""
       self.message_label.config(text="")

   def reset_all(self):
       """
       Setzt das gesamte Programm zurück.
       Löscht sämtliche CSV-Dateien (Benutzer und Einträge) und leert die GUI-Felder.
       """
       self.user_menu.set("")
       if os.path.exists(USER_FILE):
           os.remove(USER_FILE)
       if os.path.exists(DATA_FILE):
           os.remove(DATA_FILE)
       self.load_users()
       self.clear_fields()
       self.message_label.config(text="")

   # --------------------------------------------------
   # Analyse und Diagramme
   # --------------------------------------------------
   def analyze_data(self):
       """
       Führt Auswertungen durch und zeigt zwei Diagramme in einem neuen Fenster an:
        1) Modal Split (Anzahl Wege) in Prozent.
        2) Modal Split (zurückgelegte Kilometer) in Prozent.
       """
       df = load_csv(DATA_FILE)
       if df is None or df.empty:
           handle_error("Keine Daten zum Auswerten vorhanden.", self.message_label)
           return

       # Ordner für die Diagramme anlegen
       create_chart_directory()

       # 1) Modal Split (Wege in %) -> df["Modus"].value_counts(normalize=True)*100
       ways_by_mode_percent = df["Modus"].value_counts(normalize=True) * 100
       ways_chart_path = os.path.join(CHART_DIRECTORY, "modal_split_ways.png")

       plt.figure(figsize=(5, 5))
       ways_by_mode_percent.plot(
           kind="pie", autopct="%.1f%%", startangle=140
       )
       plt.title("Modal Split (Anzahl Wege in %)")
       plt.ylabel("")
       plt.tight_layout()
       plt.savefig(ways_chart_path)
       plt.close()

       # 2) Modal Split (Kilometer in %) -> Summe Distanz je Modus, dann prozentual
       km_sum_by_mode = df.groupby("Modus")["Distanz (km)"].sum()
       total_km = km_sum_by_mode.sum()
       if total_km == 0:
           # Falls alles 0 sein sollte, Fehler/Warnung
           handle_error("Keine Distanz vorhanden, Diagramm kann nicht erstellt werden.", self.message_label)
           return

       km_by_mode_percent = (km_sum_by_mode / total_km) * 100
       km_chart_path = os.path.join(CHART_DIRECTORY, "modal_split_km.png")

       plt.figure(figsize=(5, 5)) 
       km_by_mode_percent.plot(
           kind="pie", autopct="%.1f%%", startangle=140
       )
       plt.title("Modal Split (Kilometer in %)")
       plt.ylabel("")
       plt.tight_layout()
       plt.savefig(km_chart_path)
       plt.close()

       # Neues Fenster zur Anzeige der beiden Diagramme
       analysis_window = tk.Toplevel(self.root)
       analysis_window.title("Analyse Ergebnisse: Modal Split")

       try:
           ways_img = Image.open(ways_chart_path)
           ways_photo = ImageTk.PhotoImage(ways_img)
           ways_label = tk.Label(analysis_window, image=ways_photo)
           ways_label.image = ways_photo  # Referenz halten
           ways_label.pack(side=tk.LEFT, padx=10, pady=10)

           km_img = Image.open(km_chart_path)
           km_photo = ImageTk.PhotoImage(km_img)
           km_label = tk.Label(analysis_window, image=km_photo)
           km_label.image = km_photo  # Referenz halten
           km_label.pack(side=tk.LEFT, padx=10, pady=10)

       except Exception as e:
           handle_error(f"Fehler beim Laden der Diagramme: {e}", self.message_label)
           return

       show_success("Auswertung erfolgreich abgeschlossen.", self.message_label)


# --------------------------------------------------
# Hauptprogramm starten
# --------------------------------------------------
if __name__ == "__main__":
   root = tk.Tk()
   app = TrafficDiaryApp(root)
   root.mainloop()   