import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import MapBox
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.use("Agg")  # Falls auf manchen Systemen nötig, um Backend-Probleme zu vermeiden
from PIL import Image, ImageTk

# Bitte vorab installieren: pip install tkintermapview
from tkintermapview import TkinterMapView

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

def parse_or_reverse_geocode(s):
    """
    Prüft, ob 's' Koordinaten oder eine Text-Adresse ist.
    Ist es Koordinate (lat, lon) -> Reverse-Geocoding.
    Sonst -> Forward-Geocoding.
    """
    if "," in s:
        try:
            lat_str, lon_str = s.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            location = geolocator.reverse((lat, lon))
            if location:
                return (lat, lon)
            else:
                return None
        except ValueError:
            pass
    loc = geolocator.geocode(s)
    if loc:
        return (loc.latitude, loc.longitude)
    else:
        return None

def calculate_distance(start_point, end_point):
    """
    Berechnet die Distanz (in km) zwischen zwei Adressen/Koordinaten.
    """
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
        # Zeile 0: Benutzer-Auswahl
        # -----------------------------------
        ttk.Label(root, text="Benutzer/in:").grid(row=0, column=0, padx=5, pady=5)
        self.user_var = tk.StringVar()
        self.user_menu = ttk.Combobox(root, textvariable=self.user_var, state="readonly")
        self.user_menu.grid(row=0, column=1, padx=5, pady=5)

        self.load_users()

        ttk.Button(root, text="Neue/n Benutzer/in anlegen", command=self.add_new_user).grid(
            row=0, column=2, padx=5, pady=5
        )

        # -----------------------------------
        # Zeile 1: Startdatum
        # -----------------------------------
        ttk.Label(root, text="Startdatum:").grid(row=1, column=0, padx=5, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_btn = ttk.Button(root, text="Startdatum wählen", command=self.select_start_date)
        self.start_date_btn.grid(row=1, column=1, padx=5, pady=5)
        self.start_date_label = ttk.Label(root, textvariable=self.start_date_var)
        self.start_date_label.grid(row=1, column=2, padx=5, pady=5)

        # -----------------------------------
        # Zeile 2: Enddatum
        # -----------------------------------
        ttk.Label(root, text="Enddatum:").grid(row=2, column=0, padx=5, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_btn = ttk.Button(root, text="Enddatum wählen", command=self.select_end_date)
        self.end_date_btn.grid(row=2, column=1, padx=5, pady=5)
        self.end_date_label = ttk.Label(root, textvariable=self.end_date_var)
        self.end_date_label.grid(row=2, column=2, padx=5, pady=5)

        # -----------------------------------
        # Zeile 3: Startzeit
        # -----------------------------------
        ttk.Label(root, text="Startzeit:").grid(row=3, column=0, padx=5, pady=5)
        self.start_time_var = tk.StringVar()
        self.start_time_btn = ttk.Button(root, text="Startzeit wählen", command=self.select_start_time)
        self.start_time_btn.grid(row=3, column=1, padx=5, pady=5)
        self.start_time_label = ttk.Label(root, textvariable=self.start_time_var)
        self.start_time_label.grid(row=3, column=2, padx=5, pady=5)

        # -----------------------------------
        # Zeile 4: Endzeit
        # -----------------------------------
        ttk.Label(root, text="Endzeit:").grid(row=4, column=0, padx=5, pady=5)
        self.end_time_var = tk.StringVar()
        self.end_time_btn = ttk.Button(root, text="Endzeit wählen", command=self.select_end_time)
        self.end_time_btn.grid(row=4, column=1, padx=5, pady=5)
        self.end_time_label = ttk.Label(root, textvariable=self.end_time_var)
        self.end_time_label.grid(row=4, column=2, padx=5, pady=5)

        # -----------------------------------
        # Zeile 5: Startpunkt
        # -----------------------------------
        ttk.Label(root, text="Startpunkt:").grid(row=5, column=0, padx=5, pady=5)
        self.start_point_var = tk.StringVar()
        self.start_point_entry = ttk.Entry(root, textvariable=self.start_point_var)
        self.start_point_entry.grid(row=5, column=1, padx=5, pady=5)
        self.start_point_entry.bind("<Button-1>", self.open_map_for_startpoint)

        # -----------------------------------
        # Zeile 6: Endpunkt
        # -----------------------------------
        ttk.Label(root, text="Endpunkt:").grid(row=6, column=0, padx=5, pady=5)
        self.end_point_var = tk.StringVar()
        self.end_point_entry = ttk.Entry(root, textvariable=self.end_point_var)
        self.end_point_entry.grid(row=6, column=1, padx=5, pady=5)
        self.end_point_entry.bind("<Button-1>", self.open_map_for_endpoint)

        # -----------------------------------
        # Zeile 7: Verkehrsmittel
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

        # Tooltip-Fenster für Verkehrsmittel
        self.tooltip_window_mode = None
        self.question_mark_label_mode = ttk.Label(root, text="❓", foreground="blue", cursor="hand2")
        self.question_mark_label_mode.grid(row=7, column=2, padx=5, pady=5)
        self.question_mark_label_mode.bind("<Enter>", self.show_mode_tooltip)
        self.question_mark_label_mode.bind("<Leave>", self.hide_mode_tooltip)

        # -----------------------------------
        # Zeile 8: Wegezweck
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

        # Tooltip-Fenster für Wegezweck
        self.tooltip_window_purpose = None
        self.question_mark_label_purpose = ttk.Label(root, text="❓", foreground="blue", cursor="hand2")
        self.question_mark_label_purpose.grid(row=8, column=2, padx=5, pady=5)
        self.question_mark_label_purpose.bind("<Enter>", self.show_purpose_tooltip)
        self.question_mark_label_purpose.bind("<Leave>", self.hide_purpose_tooltip)

        # -----------------------------------
        # Zeile 9: Speichern-Button
        # -----------------------------------
        ttk.Button(root, text="Speichern", command=self.save_entry).grid(
            row=9, column=0, columnspan=2, padx=5, pady=10
        )

        # -----------------------------------
        # Zeile 10: Auswerten-Button
        # -----------------------------------
        ttk.Button(root, text="Jetzt auswerten", command=self.open_analysis_options).grid(
            row=10, column=0, columnspan=2, padx=5, pady=10
        )

        # -----------------------------------
        # Zeile 11: Zurücksetzen-Button
        # -----------------------------------
        ttk.Button(root, text="Zurücksetzen", command=self.reset_all).grid(
            row=11, column=0, columnspan=2, padx=5, pady=10
        )

        # -----------------------------------
        # Zeile 12: Meldungs-Label
        # -----------------------------------
        self.message_label = ttk.Label(root, text="")
        self.message_label.grid(row=12, column=0, columnspan=3, padx=5, pady=5)

        # Meldung zurücksetzen bei Änderungen
        self.start_point_var.trace_add("write", self.clear_message)
        self.end_point_var.trace_add("write", self.clear_message)
        self.mode_var.trace_add("write", self.clear_message)
        self.user_var.trace_add("write", self.clear_message)
        self.start_time_var.trace_add("write", self.clear_message)
        self.end_time_var.trace_add("write", self.clear_message)
        self.purpose_var.trace_add("write", self.clear_message)
        self.start_date_var.trace_add("write", self.clear_message)
        self.end_date_var.trace_add("write", self.clear_message)

        # --- NEU ODER GEÄNDERT: Variablen für Analyse-Zeitraum
        self.analysis_start_date_var = tk.StringVar()
        self.analysis_end_date_var = tk.StringVar()
        # -----------------------------------------------------

    # --------------------------------------------------
    # NEU: Optionen-Fenster zum Auswählen, welche Benutzer
    #      in die Auswertung einbezogen werden sollen,
    #      UND zusätzlich ein Zeitraum (Start/Enddatum).
    # --------------------------------------------------
    def open_analysis_options(self):
        """
        Öffnet ein neues Toplevel-Fenster, in dem man auswählen kann,
        welche Benutzer in die Analyse einfließen sollen.
        Zusätzlich wird ein Start- und Enddatum für den Analyse-Zeitraum abgefragt.
        """
        options_window = tk.Toplevel(self.root)
        options_window.title("Auswertung anpassen")

        checks_frame = ttk.Frame(options_window)
        checks_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(checks_frame, text="Bitte Benutzer auswählen:").pack(anchor="w", pady=(0, 5))

        self.user_check_vars = {}

        if os.path.exists(USER_FILE):
            user_df = pd.read_csv(USER_FILE)
            for _, row in user_df.iterrows():
                full_name = f"{row['Vorname']} {row['Nachname']}"
                var = tk.BooleanVar(value=True)
                chk = ttk.Checkbutton(checks_frame, text=full_name, variable=var)
                chk.pack(anchor="w", pady=2)
                self.user_check_vars[full_name] = var
        else:
            tk.Label(checks_frame, text="Keine Benutzerdatei gefunden.").pack()

        # --- NEU: Zeitraum-Frame
        period_frame = ttk.Frame(options_window)
        period_frame.pack(padx=10, pady=(0, 10), fill=tk.X, expand=True)

        tk.Label(period_frame, text="Analyse-Zeitraum auswählen:").pack(anchor="w", pady=(0, 5))

        # Startdatum
        start_frame = ttk.Frame(period_frame)
        start_frame.pack(fill=tk.X, pady=5)
        ttk.Label(start_frame, text="Startdatum:").pack(side=tk.LEFT)
        start_label = ttk.Label(start_frame, textvariable=self.analysis_start_date_var, width=12)
        start_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            start_frame,
            text="Wählen",
            command=lambda: self.select_analysis_date(self.analysis_start_date_var, "Analyse-Startdatum")
        ).pack(side=tk.LEFT)

        # Enddatum
        end_frame = ttk.Frame(period_frame)
        end_frame.pack(fill=tk.X, pady=5)
        ttk.Label(end_frame, text="Enddatum:").pack(side=tk.LEFT)
        end_label = ttk.Label(end_frame, textvariable=self.analysis_end_date_var, width=12)
        end_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            end_frame,
            text="Wählen",
            command=lambda: self.select_analysis_date(self.analysis_end_date_var, "Analyse-Enddatum")
        ).pack(side=tk.LEFT)
        # --- Ende NEU

        btn_frame = ttk.Frame(options_window)
        btn_frame.pack(padx=10, pady=10, fill=tk.X)

        def start_analysis():
            selected_users = [
                name for name, var_obj in self.user_check_vars.items() if var_obj.get()
            ]
            options_window.destroy()
            # Übergabe der neuen Zeitraums-Felder
            self.analyze_data(selected_users)

        ttk.Button(btn_frame, text="Analyse starten", command=start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=options_window.destroy).pack(side=tk.LEFT, padx=5)

    # --------------------------------------------------
    # Datumsauswahl für den Analyse-Zeitraum
    # --------------------------------------------------
    def select_analysis_date(self, variable, title):
        """
        Zeigt einen Kalender an und speichert das gewählte Datum in 'variable'.
        """
        top = tk.Toplevel(self.root)
        top.title(title)
        cal = Calendar(top, selectmode="day", date_pattern="dd.mm.yyyy")
        cal.pack(pady=10)

        def on_date_selected(event):
            date = cal.get_date()
            variable.set(date)
            top.destroy()

        cal.bind("<<CalendarSelected>>", on_date_selected)

    # --------------------------------------------------
    # Analyse und Diagramme (3 Diagramme; 2 nebeneinander, 1 darunter)
    # + Anzeige der zusätzlichen Werte
    # --------------------------------------------------
    def analyze_data(self, selected_users=None):
        """
        Führt die Datenanalyse durch.
        selected_users: Liste von Benutzer-Namen, die ausgewertet werden sollen
                        (z.B. ["Max Mustermann", "Lisa Müller", ...]).
                        Ist None oder leer, werden alle Personen ausgewertet.

        Berücksichtigt zusätzlich den Zeitraum:
        - self.analysis_start_date_var und self.analysis_end_date_var
        """
        df = load_csv(DATA_FILE)
        if df is None or df.empty:
            handle_error("Keine Daten zum Auswerten vorhanden.", self.message_label)
            return

        # --- NEU ODER GEÄNDERT: Umwandeln der Datumszeit-Spalten und Filtern nach Zeitraum
        try:
            df["Startzeit_kombiniert"] = pd.to_datetime(df["Startzeit_kombiniert"], format="%d.%m.%Y %H:%M")
        except Exception as e:
            handle_error(f"Datum/Zeit-Umwandlung fehlgeschlagen: {e}", self.message_label)
            return

        # 1) Zeitraum aus den analysis_*_date_var lesen
        analysis_start_str = self.analysis_start_date_var.get().strip()
        analysis_end_str = self.analysis_end_date_var.get().strip()

        # Nur filtern, wenn tatsächlich beide Felder belegt sind
        if analysis_start_str and analysis_end_str:
            try:
                analysis_start_dt = datetime.strptime(analysis_start_str, "%d.%m.%Y")
                analysis_end_dt = datetime.strptime(analysis_end_str, "%d.%m.%Y")
                # Ende des Tages: 23:59:59
                analysis_end_dt = analysis_end_dt.replace(hour=23, minute=59, second=59)

                # Filter: hier Beispiel, nur Startzeiten im Bereich
                df = df[df["Startzeit_kombiniert"] >= analysis_start_dt]
                df = df[df["Startzeit_kombiniert"] <= analysis_end_dt]

            except ValueError:
                handle_error("Analyse-Zeitraum ungültig oder nicht vollständig.", self.message_label)
                return

            if df.empty:
                handle_error("Keine Einträge im ausgewählten Zeitraum gefunden.", self.message_label)
                return
        # --- Ende NEU

        df["Distanz (km)"] = pd.to_numeric(df["Distanz (km)"], errors="coerce")

        # Benutzer-Filter
        if selected_users:
            df = df[df["Benutzer/in"].isin(selected_users)]
            if df.empty:
                handle_error("Keine Einträge für die gewählten Benutzer/innen vorhanden.", self.message_label)
                return

        create_chart_directory()

        # --- 1) Modal Split (Anzahl Wege in %) ---
        color_map_mode = {
            "MIV": "red",
            "MIV-Mitfahrer": "orange",
            "Fuß": "lightskyblue",
            "Fahrrad": "darkblue",
            "ÖV": "green",
            "Sonstiges": "pink"
        }
        ways_by_mode_percent = df["Modus"].value_counts(normalize=True) * 100
        ways_modes = ways_by_mode_percent.index
        ways_colors = [color_map_mode.get(m, "grey") for m in ways_modes]

        ways_chart_path = os.path.join(CHART_DIRECTORY, "modal_split_ways.png")
        plt.figure(figsize=(6, 6))
        plt.pie(
            ways_by_mode_percent,
            labels=ways_modes,
            autopct="%.1f%%",
            startangle=140,
            colors=ways_colors
        )
        plt.title("Modal Split Wege", fontsize=14, fontweight="bold")
        plt.figtext(0.5, 0.01, "Angaben in Prozent", ha="center", fontsize=10)
        plt.tight_layout()
        plt.savefig(ways_chart_path)
        plt.close()

        # --- 2) Modal Split Personenkilometer ---
        km_sum_by_mode = df.groupby("Modus")["Distanz (km)"].sum()
        total_km = km_sum_by_mode.sum()
        if total_km == 0:
            handle_error("Keine Distanz vorhanden, Diagramm kann nicht erstellt werden.", self.message_label)
            return

        km_by_mode_percent = (km_sum_by_mode / total_km) * 100
        km_modes = km_by_mode_percent.index
        km_colors = [color_map_mode.get(m, "grey") for m in km_modes]

        km_chart_path = os.path.join(CHART_DIRECTORY, "modal_split_km.png")
        plt.figure(figsize=(6, 6))
        plt.pie(
            km_by_mode_percent,
            labels=km_modes,
            autopct="%.1f%%",
            startangle=140,
            colors=km_colors
        )
        plt.title("Modal Split Personenkilometer", fontsize=14, fontweight="bold")
        plt.figtext(0.5, 0.01, "Angaben in Prozent", ha="center", fontsize=10)
        plt.tight_layout()
        plt.savefig(km_chart_path)
        plt.close()

        # --- 3) Verkehrsaufkommen (Wege) ---
        color_map_purpose = {
            "Arbeit": "lightskyblue",
            "Dienstlich": "blue",
            "Ausbildung": "darkblue",
            "Einkauf": "brown",
            "Erledigung": "red",
            "Freizeit": "yellow",
            "Begleitung": "lightgreen"
        }
        wegezweck_counts = df["Wegezweck"].value_counts(normalize=True) * 100
        wegezweck_list = wegezweck_counts.index
        wegezweck_colors = [color_map_purpose.get(wz, "grey") for wz in wegezweck_list]

        wegezweck_chart_path = os.path.join(CHART_DIRECTORY, "verkehrsaufkommen_wege.png")
        plt.figure(figsize=(6, 6))
        plt.pie(
            wegezweck_counts,
            labels=wegezweck_list,
            autopct="%.1f%%",
            startangle=140,
            colors=wegezweck_colors
        )
        plt.title("Verkehrsaufkommen (Wege)", fontsize=14, fontweight="bold")
        plt.figtext(0.5, 0.01, "Angaben in Prozent", ha="center", fontsize=10)
        plt.tight_layout()
        plt.savefig(wegezweck_chart_path)
        plt.close()

        # ---------------------------------------
        # Scrollbares Fenster für die Diagramme
        # ---------------------------------------
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Analyse Ergebnisse: Modal Split und Verkehrsaufkommen")

        container = ttk.Frame(analysis_window)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        diagrams_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=diagrams_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        diagrams_frame.bind("<Configure>", on_frame_configure)

        def _on_mousewheel(event):
            if event.delta:  # Windows/Mac
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:  # Linux
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

        diagrams_frame.bind("<MouseWheel>", _on_mousewheel)
        diagrams_frame.bind("<Button-4>", _on_mousewheel)
        diagrams_frame.bind("<Button-5>", _on_mousewheel)

        # ---------------------------------------
        # Oberer Bereich (2 Diagramme nebeneinander)
        # ---------------------------------------
        upper_frame = ttk.Frame(diagrams_frame)
        # Bündig: gleicher Innenabstand links/rechts wie unten
        upper_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        try:
            # Modal Split Wege (links)
            ways_img = Image.open(ways_chart_path)
            ways_photo = ImageTk.PhotoImage(ways_img)
            ways_label = tk.Label(upper_frame, image=ways_photo)
            ways_label.image = ways_photo
            ways_label.pack(side=tk.LEFT, anchor="n", padx=0)

            # Modal Split Personenkilometer (rechts)
            km_img = Image.open(km_chart_path)
            km_photo = ImageTk.PhotoImage(km_img)
            km_label = tk.Label(upper_frame, image=km_photo)
            km_label.image = km_photo
            km_label.pack(side=tk.LEFT, anchor="n", padx=40)  # etwas Abstand nach rechts
        except Exception as e:
            handle_error(f"Fehler beim Laden der Diagramme: {e}", self.message_label)
            return

        # ---------------------------------------
        # Unterer Bereich (Diagramm + Werte nebeneinander)
        # ---------------------------------------
        lower_frame = ttk.Frame(diagrams_frame)
        lower_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Linke Spalte: Verkehrsaufkommen (Wege)
        lower_left_frame = ttk.Frame(lower_frame)
        lower_left_frame.pack(side=tk.LEFT, anchor="n")

        # Rechte Spalte: Statistikwerte
        lower_right_frame = ttk.Frame(lower_frame)
        lower_right_frame.pack(side=tk.LEFT, anchor="n", padx=40)

        # Verkehrsaufkommen (Wege)-Diagramm
        try:
            wz_img = Image.open(wegezweck_chart_path)
            wz_photo = ImageTk.PhotoImage(wz_img)
            wz_label = tk.Label(lower_left_frame, image=wz_photo)
            wz_label.image = wz_photo
            wz_label.pack(side=tk.TOP, anchor="n")
        except Exception as e:
            handle_error(f"Fehler beim Laden des Diagramms 'Verkehrsaufkommen (Wege)': {e}", self.message_label)
            return

        # ---------------------------------------
        # Statistikwerte (rechts neben dem Diagramm "Verkehrsaufkommen (Wege)")
        # ---------------------------------------
        # Anzahl der verschiedenen Tage in der Auswahl
        day_count = df["Startzeit_kombiniert"].dt.date.nunique()
        # Gesamtzahl an Wegen
        number_of_ways = len(df)
        # Gesamtdistanz
        total_distance = df["Distanz (km)"].sum()

        if day_count > 0:
            avg_ways = number_of_ways / day_count
            avg_distance = total_distance / day_count
        else:
            # Falls doch kein Tag vorhanden, zur Sicherheit abfangen
            avg_ways = 0
            avg_distance = 0

        # Überschrift in schwarzer, fetter Schrift
        headline_label = ttk.Label(
            lower_right_frame,
            text="Durchschnittliche Tageswerte",
            font=("Helvetica", 14, "bold"),
            foreground="black"
        )
        headline_label.pack(side=tk.TOP, padx=0, pady=(0, 10), anchor="w")

        # Durchschnittliche Wegeanzahl (normal, schwarz)
        label_avg_ways = ttk.Label(
            lower_right_frame,
            text=f"Durchschnittliche Wegeanzahl pro Tag: {avg_ways:.2f}",
            font=("Helvetica", 12),
            foreground="black"
        )
        label_avg_ways.pack(side=tk.TOP, padx=0, pady=5, anchor="w")

        # Durchschnittliche Distanz (normal, schwarz)
        label_avg_distance = ttk.Label(
            lower_right_frame,
            text=f"Durchschnittlich zurückgelegte Strecke (km/Tag): {avg_distance:.2f}",
            font=("Helvetica", 12),
            foreground="black"
        )
        label_avg_distance.pack(side=tk.TOP, padx=0, pady=5, anchor="w")

        show_success("Auswertung erfolgreich abgeschlossen.", self.message_label)

    # --------------------------------------------------
    # Benutzer-Funktionen
    # --------------------------------------------------
    def load_users(self):
        self.user_menu['values'] = []
        if os.path.exists(USER_FILE):
            users = pd.read_csv(USER_FILE)
            user_list = sorted(users["Vorname"] + " " + users["Nachname"])
            self.user_menu['values'] = user_list

    def add_new_user(self):
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

        first_name_entry.focus()
        user_window.bind("<Return>", save_user)

    # --------------------------------------------------
    # Tooltip-Methoden für Verkehrsmittel / Wegezweck
    # --------------------------------------------------
    def show_mode_tooltip(self, event):
        if self.tooltip_window_mode is not None:
            return
        self.tooltip_window_mode = tk.Toplevel(self.root)
        self.tooltip_window_mode.wm_overrideredirect(True)

        x = event.x_root
        y = event.y_root + 20
        self.tooltip_window_mode.geometry(f"+{x}+{y}")

        table_frame = tk.Frame(self.tooltip_window_mode, background="white", relief="solid", borderwidth=1)
        table_frame.pack()

        header_text = f"{'Verkehrsmittel':<15}{'Hierzu gehören':<40}"
        header_label = tk.Label(table_frame, text=header_text, font=("Consolas", 10, "bold"),
                                background="white", justify="left")
        header_label.pack(anchor="w", padx=5, pady=(5, 2))

        body_text = (
            f"{'Fahrrad':<15}Pedelecs, E-Bikes, Lastenräder, E-Scooter etc.\n"
            f"{'Fuß':<15}Fußbus\n"
            f"{'MIV':<15}Auto, Transporter etc.\n"
            f"{'MIV-Mitfahrer':<15}Mitfahrten, Taxifahrten etc.\n"
            f"{'Sonstiges':<15}Schiff, Flugzeug, Rakete etc.\n"
            f"{'ÖV':<15}Nahverkehr (Bus, Straßenbahn, RB), Fernverkehr (ICE, TGV, Flixtrain, Westbahn, Fernbus) etc.\n"
        )
        body_label = tk.Label(table_frame, text=body_text, font=("Consolas", 10),
                              background="white", justify="left")
        body_label.pack(anchor="w", padx=5, pady=(0, 5))

    def hide_mode_tooltip(self, event):
        if self.tooltip_window_mode is not None:
            self.tooltip_window_mode.destroy()
            self.tooltip_window_mode = None

    def show_purpose_tooltip(self, event):
        if self.tooltip_window_purpose is not None:
            return
        self.tooltip_window_purpose = tk.Toplevel(self.root)
        self.tooltip_window_purpose.wm_overrideredirect(True)

        x = event.x_root
        y = event.y_root + 20
        self.tooltip_window_purpose.geometry(f"+{x}+{y}")

        table_frame = tk.Frame(self.tooltip_window_purpose, background="white", relief="solid", borderwidth=1)
        table_frame.pack()

        header_text = f"{'Wegezweck':<12}{'Beispiel'}"
        header_label = tk.Label(table_frame, text=header_text, font=("Consolas", 10, "bold"),
                                background="white", justify="left")
        header_label.pack(anchor="w", padx=5, pady=(5, 2))

        body_text = (
            f"{'Arbeit':<12}Weg zur Arbeitsstätte\n"
            f"{'Ausbildung':<12}Universität, Schule etc.\n"
            f"{'Begleitung':<12}Kind zur Schule bringen\n"
            f"{'Dienstlich':<12}Dienstreise, Weg während der Arbeit\n"
            f"{'Einkauf':<12}Supermarkt\n"
            f"{'Erledigung':<12}Arztbesuch\n"
            f"{'Freizeit':<12}Nach Hause, Sport, Freunde etc.\n\n"
            "Wege zurück nach Hause sind immer Freizeit-Wege!"
        )
        body_label = tk.Label(table_frame, text=body_text, font=("Consolas", 10),
                              background="white", justify="left")
        body_label.pack(anchor="w", padx=5, pady=(0, 5))

    def hide_purpose_tooltip(self, event):
        if self.tooltip_window_purpose is not None:
            self.tooltip_window_purpose.destroy()
            self.tooltip_window_purpose = None

    # --------------------------------------------------
    # Methoden für Kalender/Uhrzeit (Wege-Eintrag)
    # --------------------------------------------------
    def select_start_date(self):
        self.select_date(self.start_date_var, "Startdatum")

    def select_end_date(self):
        self.select_date(self.end_date_var, "Enddatum")

    def select_date(self, variable, title):
        top = tk.Toplevel(self.root)
        top.title(title)
        cal = Calendar(top, selectmode="day", date_pattern="dd.mm.yyyy")
        cal.pack(pady=10)

        def on_date_selected(event):
            date = cal.get_date()
            variable.set(date)
            top.destroy()

        cal.bind("<<CalendarSelected>>", on_date_selected)

    def select_start_time(self):
        self.select_time(self.start_time_var, "Startzeit")

    def select_end_time(self):
        self.select_time(self.end_time_var, "Endzeit")

    def select_time(self, variable, title):
        top = tk.Toplevel(self.root)
        top.title(title)

        time_frame = ttk.Frame(top)
        time_frame.pack(padx=10, pady=10)

        ttk.Label(time_frame, text="Stunde (00-23):").grid(row=0, column=0, padx=5, pady=5)
        hour_var = tk.StringVar()
        hour_entry = ttk.Entry(time_frame, textvariable=hour_var, width=2)
        hour_entry.grid(row=0, column=1, padx=2, pady=5)

        ttk.Label(time_frame, text=":").grid(row=0, column=2, padx=2, pady=5)

        ttk.Label(time_frame, text="Minute (00-59):").grid(row=0, column=3, padx=5, pady=5)
        minute_var = tk.StringVar()
        minute_entry = ttk.Entry(time_frame, textvariable=minute_var, width=2)
        minute_entry.grid(row=0, column=4, padx=2, pady=5)

        def confirm_time(event=None):
            h = hour_var.get()
            m = minute_var.get()
            if len(h) != 2 or len(m) != 2:
                handle_error("Bitte 2 Ziffern für Stunde und Minute eingeben.", self.message_label)
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
            time_str = f"{h}:{m}"
            variable.set(time_str)
            top.destroy()

        top.bind("<Return>", confirm_time)

        ttk.Button(time_frame, text="OK", command=confirm_time).grid(
            row=1, column=0, columnspan=5, pady=8
        )

        hour_entry.focus()

    # --------------------------------------------------
    # Karte
    # --------------------------------------------------
    def open_map_for_startpoint(self, event=None):
        self.open_map_generic(
            var_name="start_point",
            window_title="Startpunkt wählen",
            confirm_btn_text="Diesen Startpunkt übernehmen"
        )

    def open_map_for_endpoint(self, event=None):
        self.open_map_generic(
            var_name="end_point",
            window_title="Endpunkt wählen",
            confirm_btn_text="Diesen Endpunkt übernehmen"
        )

    def open_map_generic(self, var_name, window_title, confirm_btn_text):
        map_window = tk.Toplevel(self.root)
        map_window.title(window_title)

        style = ttk.Style(map_window)
        style.configure("BigButton.TButton", font=("Arial", 12, "bold"), padding=6)

        search_frame = ttk.Frame(map_window)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        def search_location():
            nonlocal marker
            query = search_var.get().strip()
            if not query:
                return
            if marker is not None:
                handle_error("Ein Marker existiert bereits. Bitte 'Marker zurücksetzen'.", self.message_label)
                return
            try:
                loc = geolocator.geocode(query)
                if loc:
                    map_widget.set_position(loc.latitude, loc.longitude)
                    map_widget.set_zoom(14)
                    marker = map_widget.set_marker(loc.latitude, loc.longitude, text="")
                    marker.set_marker_color("red")
                    disable_left_click()
                else:
                    handle_error("Adresse nicht gefunden.", self.message_label)
            except Exception as e:
                handle_error(f"Fehler bei der Ortssuche: {e}", self.message_label)

        search_button = ttk.Button(search_frame, text="Suchen", command=search_location)
        search_button.pack(side=tk.LEFT, padx=5)

        action_frame = ttk.Frame(map_window)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        map_widget = TkinterMapView(map_window, width=800, height=600, corner_radius=0)
        map_widget.set_tile_server(
            f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_API_KEY}",
            tile_size=512,
            max_zoom=19
        )

        karlsruhe_lat, karlsruhe_lon = 49.00937, 8.40444
        map_widget.set_position(karlsruhe_lat, karlsruhe_lon)
        map_widget.set_zoom(12)

        marker = None

        def disable_left_click():
            map_widget.remove_left_click_map_command(on_map_click)

        def enable_left_click():
            map_widget.add_left_click_map_command(on_map_click)

        def on_map_click(coordinate):
            nonlocal marker
            if marker is not None:
                handle_error("Ein Marker existiert bereits. Bitte 'Marker zurücksetzen'.", self.message_label)
                return
            lat, lon = coordinate
            marker = map_widget.set_marker(lat, lon, text="")
            marker.set_marker_color("red")
            disable_left_click()

        enable_left_click()

        def reset_marker():
            nonlocal marker
            if marker:
                marker.delete()
                marker = None
            enable_left_click()

        def confirm_selection():
            if marker:
                lat, lon = marker.position
                coord_str = f"{lat:.5f}, {lon:.5f}"
                if var_name == "start_point":
                    self.start_point_var.set(coord_str)
                else:
                    self.end_point_var.set(coord_str)
            map_window.destroy()

        reset_btn = ttk.Button(action_frame, text="Marker zurücksetzen", command=reset_marker, style="BigButton.TButton")
        reset_btn.pack(side=tk.LEFT, padx=10)

        confirm_btn = ttk.Button(action_frame, text=confirm_btn_text, command=confirm_selection, style="BigButton.TButton")
        confirm_btn.pack(side=tk.RIGHT, padx=10)

        map_widget.pack(fill=tk.BOTH, expand=True)

    # --------------------------------------------------
    # Speichern, Zurücksetzen usw.
    # --------------------------------------------------
    def save_entry(self):
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

        start_datetime_str = f"{start_date} {start_time}"
        end_datetime_str = f"{end_date} {end_time}"

        try:
            start_dt = datetime.strptime(start_datetime_str, "%d.%m.%Y %H:%M")
            end_dt = datetime.strptime(end_datetime_str, "%d.%m.%Y %H:%M")
        except ValueError:
            handle_error("Datum/Zeit-Format ist ungültig. Bitte Format TT.MM.YYYY HH:MM verwenden.", self.message_label)
            return

        if end_dt < start_dt:
            handle_error(
                "Enddatum/-zeit liegt vor Startdatum/-zeit. Bitte prüfen, ob das Enddatum evtl. am Folgetag angegeben ist.",
                self.message_label
            )
            return

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
            "Startzeit_kombiniert": start_datetime_str,
            "Endzeit_kombiniert": end_datetime_str,
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
        self.message_label.config(text="")

    def reset_all(self):
        """
        Setzt alle Felder zurück und entfernt (falls vorhanden) die User- und Daten-Dateien.
        Zusätzlich werden alle Dateien im Ordner "charts" gelöscht, der Ordner selbst bleibt aber bestehen.
        """
        self.user_menu.set("")
        
        # USER_FILE und DATA_FILE löschen
        if os.path.exists(USER_FILE):
            os.remove(USER_FILE)
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        
        # Alle Dateien im Ordner CHART_DIRECTORY löschen
        if os.path.exists(CHART_DIRECTORY):
            for filename in os.listdir(CHART_DIRECTORY):
                file_path = os.path.join(CHART_DIRECTORY, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass  # Fehler beim Löschen ignorieren
        
        self.load_users()
        self.clear_fields()
        self.message_label.config(text="")

# --------------------------------------------------
# Hauptprogramm starten
# --------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficDiaryApp(root)
    root.mainloop()