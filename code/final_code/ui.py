# This module is the core of our application.
# It manages the graphical user interface, data entry, tooltips and map interactions via Tkinter.

import pandas as pd
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageTk
from datetime import datetime
from tkintermapview import TkinterMapView

# Matplotlib-Backend einstellen (falls nötig für headless-Umgebungen)
matplotlib.use("Agg")

# ---- Importiere alles, was wir aus logic.py brauchen ----
from logic import (
    DATA_FILE, USER_FILE, CHART_DIRECTORY, MAPBOX_API_KEY,
    handle_error, show_success, create_chart_directory,
    parse_or_reverse_geocode, calculate_distance,
    save_to_csv, load_csv, geolocator
)


class TrafficDiaryApp:
    """
    Hauptklasse für das Tkinter-Programm.
    Enthält GUI-Elemente und zugehörige Logik.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Diary Analysis Tool")

        # ------------------ GUI-Elemente: Zeile 0, Benutzerwahl ------------------
        ttk.Label(root, text="Benutzer/in:").grid(row=0, column=0, padx=5, pady=5)
        self.user_var = tk.StringVar()
        self.user_menu = ttk.Combobox(root, textvariable=self.user_var, state="readonly")
        self.user_menu.grid(row=0, column=1, padx=5, pady=5)
        self.load_users()

        ttk.Button(
            root,
            text="Neue/n Benutzer/in anlegen",
            command=self.add_new_user
        ).grid(row=0, column=2, padx=5, pady=5)

        # ------------------ GUI-Elemente: Datums- und Uhrzeitwahl ------------------
        ttk.Label(root, text="Startdatum:").grid(row=1, column=0, padx=5, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_btn = ttk.Button(root, text="Startdatum wählen", command=self.select_start_date)
        self.start_date_btn.grid(row=1, column=1, padx=5, pady=5)
        self.start_date_label = ttk.Label(root, textvariable=self.start_date_var)
        self.start_date_label.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(root, text="Enddatum:").grid(row=2, column=0, padx=5, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_btn = ttk.Button(root, text="Enddatum wählen", command=self.select_end_date)
        self.end_date_btn.grid(row=2, column=1, padx=5, pady=5)
        self.end_date_label = ttk.Label(root, textvariable=self.end_date_var)
        self.end_date_label.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(root, text="Startzeit:").grid(row=3, column=0, padx=5, pady=5)
        self.start_time_var = tk.StringVar()
        self.start_time_btn = ttk.Button(root, text="Startzeit wählen", command=self.select_start_time)
        self.start_time_btn.grid(row=3, column=1, padx=5, pady=5)
        self.start_time_label = ttk.Label(root, textvariable=self.start_time_var)
        self.start_time_label.grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(root, text="Endzeit:").grid(row=4, column=0, padx=5, pady=5)
        self.end_time_var = tk.StringVar()
        self.end_time_btn = ttk.Button(root, text="Endzeit wählen", command=self.select_end_time)
        self.end_time_btn.grid(row=4, column=1, padx=5, pady=5)
        self.end_time_label = ttk.Label(root, textvariable=self.end_time_var)
        self.end_time_label.grid(row=4, column=2, padx=5, pady=5)

        # ------------------ GUI-Elemente: Start- und Endpunkt ------------------
        ttk.Label(root, text="Startpunkt:").grid(row=5, column=0, padx=5, pady=5)
        self.start_point_var = tk.StringVar()
        self.start_point_entry = ttk.Entry(root, textvariable=self.start_point_var)
        self.start_point_entry.grid(row=5, column=1, padx=5, pady=5)
        self.start_point_entry.bind("<Button-1>", self.open_map_for_startpoint)

        ttk.Label(root, text="Endpunkt:").grid(row=6, column=0, padx=5, pady=5)
        self.end_point_var = tk.StringVar()
        self.end_point_entry = ttk.Entry(root, textvariable=self.end_point_var)
        self.end_point_entry.grid(row=6, column=1, padx=5, pady=5)
        self.end_point_entry.bind("<Button-1>", self.open_map_for_endpoint)

        # ------------------ GUI-Elemente: Verkehrsmittel & Wegezweck ------------------
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

        # Tooltip-Verkehrsmittel
        self.tooltip_window_mode = None
        self.question_mark_label_mode = ttk.Label(root, text="❓", foreground="blue", cursor="hand2")
        self.question_mark_label_mode.grid(row=7, column=2, padx=5, pady=5)
        self.question_mark_label_mode.bind("<Enter>", self.show_mode_tooltip)
        self.question_mark_label_mode.bind("<Leave>", self.hide_mode_tooltip)

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

        # Tooltip-Wegezweck
        self.tooltip_window_purpose = None
        self.question_mark_label_purpose = ttk.Label(root, text="❓", foreground="blue", cursor="hand2")
        self.question_mark_label_purpose.grid(row=8, column=2, padx=5, pady=5)
        self.question_mark_label_purpose.bind("<Enter>", self.show_purpose_tooltip)
        self.question_mark_label_purpose.bind("<Leave>", self.hide_purpose_tooltip)

        # ------------------ GUI-Elemente: Buttons & Meldungslabel ------------------
        ttk.Button(root, text="Speichern", command=self.save_entry).grid(row=9, column=0, columnspan=2, padx=5, pady=10)
        ttk.Button(root, text="Jetzt auswerten", command=self.open_analysis_options).grid(row=10, column=0, columnspan=2, padx=5, pady=10)
        ttk.Button(root, text="Zurücksetzen", command=self.reset_all).grid(row=11, column=0, columnspan=2, padx=5, pady=10)

        self.message_label = ttk.Label(root, text="")
        self.message_label.grid(row=12, column=0, columnspan=3, padx=5, pady=5)

        # Meldung zurücksetzen, wenn sich Werte ändern
        self.start_point_var.trace_add("write", self.clear_message)
        self.end_point_var.trace_add("write", self.clear_message)
        self.mode_var.trace_add("write", self.clear_message)
        self.user_var.trace_add("write", self.clear_message)
        self.start_time_var.trace_add("write", self.clear_message)
        self.end_time_var.trace_add("write", self.clear_message)
        self.purpose_var.trace_add("write", self.clear_message)
        self.start_date_var.trace_add("write", self.clear_message)
        self.end_date_var.trace_add("write", self.clear_message)

        # Zusätzliche Variablen für den Analysezeitraum
        self.analysis_start_date_var = tk.StringVar()
        self.analysis_end_date_var = tk.StringVar()

    # ---------------------------------------------------------------------------
    #                           Analyse-Optionen
    # ---------------------------------------------------------------------------
    def open_analysis_options(self):
        """Öffnet ein neues Fenster zur Auswahl der Benutzer/innen und des Analyse-Zeitraums."""
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

        # Zeitraum-Frame
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
            command=lambda: self.select_analysis_date(self.analysis_start_date_var, "Analyse-Startdatum"),
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
            command=lambda: self.select_analysis_date(self.analysis_end_date_var, "Analyse-Enddatum"),
        ).pack(side=tk.LEFT)

        btn_frame = ttk.Frame(options_window)
        btn_frame.pack(padx=10, pady=10, fill=tk.X)

        def start_analysis():
            selected_users = [
                name for name, var_obj in self.user_check_vars.items() if var_obj.get()
            ]
            options_window.destroy()
            self.analyze_data(selected_users)

        ttk.Button(btn_frame, text="Analyse starten", command=start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Abbrechen", command=options_window.destroy).pack(side=tk.LEFT, padx=5)

    def select_analysis_date(self, variable, title):
        """Zeigt einen Kalender an und speichert das gewählte Datum in 'variable'."""
        top = tk.Toplevel(self.root)
        top.title(title)
        cal = Calendar(top, selectmode="day", date_pattern="dd.mm.yyyy")
        cal.pack(pady=10)

        def on_date_selected(event):
            date = cal.get_date()
            variable.set(date)
            top.destroy()

        cal.bind("<<CalendarSelected>>", on_date_selected)

    # ---------------------------------------------------------------------------
    #                       Analyse & Diagrammerstellung
    # ---------------------------------------------------------------------------
    def analyze_data(self, selected_users=None):
        """
        Führt die Datenanalyse durch und zeigt die Diagramme in einem Scroll-Fenster an.
        - selected_users: Liste der ausgewählten Benutzer/innen.
        - Zusätzlich wird der Zeitraum aus den Variablen analysis_start_date_var / analysis_end_date_var gelesen.
        """
        df = load_csv(DATA_FILE)
        if df is None or df.empty:
            handle_error("Keine Daten zum Auswerten vorhanden.", self.message_label)
            return

        # Datums-Umwandlung
        try:
            df["Startzeit_kombiniert"] = pd.to_datetime(df["Startzeit_kombiniert"], format="%d.%m.%Y %H:%M")
        except Exception as e:
            handle_error(f"Datum/Zeit-Umwandlung fehlgeschlagen: {e}", self.message_label)
            return

        # Zeitraum filtern
        analysis_start_str = self.analysis_start_date_var.get().strip()
        analysis_end_str = self.analysis_end_date_var.get().strip()
        if analysis_start_str and analysis_end_str:
            try:
                analysis_start_dt = datetime.strptime(analysis_start_str, "%d.%m.%Y")
                analysis_end_dt = datetime.strptime(analysis_end_str, "%d.%m.%Y")
                analysis_end_dt = analysis_end_dt.replace(hour=23, minute=59, second=59)

                df = df[df["Startzeit_kombiniert"] >= analysis_start_dt]
                df = df[df["Startzeit_kombiniert"] <= analysis_end_dt]
            except ValueError:
                handle_error("Analyse-Zeitraum ungültig oder unvollständig.", self.message_label)
                return

            if df.empty:
                handle_error("Keine Einträge im ausgewählten Zeitraum gefunden.", self.message_label)
                return

        # Distanzspalte in numerisches Format
        df["Distanz (km)"] = pd.to_numeric(df["Distanz (km)"], errors="coerce")

        # Filter nach Benutzern
        if selected_users:
            df = df[df["Benutzer/in"].isin(selected_users)]
            if df.empty:
                handle_error("Keine Einträge für die gewählten Benutzer/innen.", self.message_label)
                return

        # Ordner für Diagramme sicherstellen
        create_chart_directory()

        # 1) Modal Split (Wege in %)
        color_map_mode = {
            "MIV": "red",
            "MIV-Mitfahrer": "orange",
            "Fuß": "lightskyblue",
            "Fahrrad": "darkblue",
            "ÖV": "green",
            "Sonstiges": "pink",
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
            colors=ways_colors,
        )
        plt.title("Modal Split Wege", fontsize=14, fontweight="bold")
        plt.figtext(0.5, 0.01, "Angaben in Prozent", ha="center", fontsize=10)
        plt.tight_layout()
        plt.savefig(ways_chart_path)
        plt.close()

        # 2) Modal Split Personenkilometer
        km_sum_by_mode = df.groupby("Modus")["Distanz (km)"].sum()
        total_km = km_sum_by_mode.sum()
        if total_km == 0:
            handle_error("Keine Distanz vorhanden, kein Diagramm möglich.", self.message_label)
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
            colors=km_colors,
        )
        plt.title("Modal Split Personenkilometer", fontsize=14, fontweight="bold")
        plt.figtext(0.5, 0.01, "Angaben in Prozent", ha="center", fontsize=10)
        plt.tight_layout()
        plt.savefig(km_chart_path)
        plt.close()

        # 3) Verkehrsaufkommen (Wege)
        color_map_purpose = {
            "Arbeit": "lightskyblue",
            "Dienstlich": "blue",
            "Ausbildung": "darkblue",
            "Einkauf": "brown",
            "Erledigung": "red",
            "Freizeit": "yellow",
            "Begleitung": "lightgreen",
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
            colors=wegezweck_colors,
        )
        plt.title("Verkehrsaufkommen (Wege)", fontsize=14, fontweight="bold")
        plt.figtext(0.5, 0.01, "Angaben in Prozent", ha="center", fontsize=10)
        plt.tight_layout()
        plt.savefig(wegezweck_chart_path)
        plt.close()

        # ------------ Neues Fenster mit den Diagrammen (scrollbar) ------------
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
            """Ermöglicht das Scrollen per Mausrad (auch für Linux)."""
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

        # --- Oberer Bereich (zwei Diagramme nebeneinander) ---
        upper_frame = ttk.Frame(diagrams_frame)
        upper_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        try:
            ways_img = Image.open(ways_chart_path)
            ways_photo = ImageTk.PhotoImage(ways_img)
            ways_label = tk.Label(upper_frame, image=ways_photo)
            ways_label.image = ways_photo
            ways_label.pack(side=tk.LEFT, anchor="n")

            km_img = Image.open(km_chart_path)
            km_photo = ImageTk.PhotoImage(km_img)
            km_label = tk.Label(upper_frame, image=km_photo)
            km_label.image = km_photo
            km_label.pack(side=tk.LEFT, anchor="n", padx=40)
        except Exception as e:
            handle_error(f"Fehler beim Laden der Diagramme: {e}", self.message_label)
            return

        # --- Unterer Bereich (drittes Diagramm + Kennwerte) ---
        lower_frame = ttk.Frame(diagrams_frame)
        lower_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        lower_left_frame = ttk.Frame(lower_frame)
        lower_left_frame.pack(side=tk.LEFT, anchor="n")

        lower_right_frame = ttk.Frame(lower_frame)
        lower_right_frame.pack(side=tk.LEFT, anchor="n", padx=40)

        try:
            wz_img = Image.open(wegezweck_chart_path)
            wz_photo = ImageTk.PhotoImage(wz_img)
            wz_label = tk.Label(lower_left_frame, image=wz_photo)
            wz_label.image = wz_photo
            wz_label.pack(side=tk.TOP, anchor="n")
        except Exception as e:
            handle_error(f"Fehler beim Laden des Diagramms 'Verkehrsaufkommen (Wege)': {e}", self.message_label)
            return

        # Statistikwerte berechnen
        day_count = df["Startzeit_kombiniert"].dt.date.nunique()
        number_of_ways = len(df)
        total_distance = df["Distanz (km)"].sum()

        if day_count > 0:
            avg_ways = number_of_ways / day_count
            avg_distance = total_distance / day_count
        else:
            avg_ways = 0
            avg_distance = 0

        headline_label = ttk.Label(
            lower_right_frame,
            text="Durchschnittliche Tageswerte",
            font=("Helvetica", 14, "bold"),
            foreground="black"
        )
        headline_label.pack(side=tk.TOP, pady=(0, 10), anchor="w")

        label_avg_ways = ttk.Label(
            lower_right_frame,
            text=f"Durchschnittliche Wegeanzahl pro Tag: {avg_ways:.2f}",
            font=("Helvetica", 12),
            foreground="black"
        )
        label_avg_ways.pack(side=tk.TOP, pady=5, anchor="w")

        label_avg_distance = ttk.Label(
            lower_right_frame,
            text=f"Durchschnittlich zurückgelegte Strecke (km/Tag): {avg_distance:.2f}",
            font=("Helvetica", 12),
            foreground="black"
        )
        label_avg_distance.pack(side=tk.TOP, pady=5, anchor="w")

        show_success("Auswertung erfolgreich abgeschlossen.", self.message_label)

    # ---------------------------------------------------------------------------
    #                         Benutzer-Funktionen
    # ---------------------------------------------------------------------------
    def load_users(self):
        """Lädt vorhandene Benutzer/innen aus der CSV-Datei und füllt das Combobox-Menü."""
        self.user_menu["values"] = []
        if os.path.exists(USER_FILE):
            users = pd.read_csv(USER_FILE)
            user_list = sorted(users["Vorname"] + " " + users["Nachname"])
            self.user_menu["values"] = user_list

    def add_new_user(self):
        """Öffnet ein Fenster zum Anlegen eines neuen Benutzers/einer neuen Benutzerin."""

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
                    existing_users["Vorname"].str.lower()
                    + " "
                    + existing_users["Nachname"].str.lower()
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

    # ---------------------------------------------------------------------------
    #                 Tooltip-Methoden für Verkehrsmittel / Wegezweck
    # ---------------------------------------------------------------------------
    def show_mode_tooltip(self, event):
        """Zeigt einen Tooltip für Verkehrsmittel."""
        if self.tooltip_window_mode is not None:
            return
        self.tooltip_window_mode = tk.Toplevel(self.root)
        self.tooltip_window_mode.wm_overrideredirect(True)

        x = event.x_root
        y = event.y_root + 20
        self.tooltip_window_mode.geometry(f"+{x}+{y}")

        table_frame = tk.Frame(self.tooltip_window_mode, background="white", relief="solid", borderwidth=1)
        table_frame.pack()

        header_label = tk.Label(
            table_frame,
            text=f"{'Verkehrsmittel':<15}{'Hierzu gehören':<40}",
            font=("Consolas", 10, "bold"),
            background="white",
            justify="left"
        )
        header_label.pack(anchor="w", padx=5, pady=(5, 2))

        body_text = (
            f"{'Fahrrad':<15}Pedelecs, E-Bikes, Lastenräder, E-Scooter etc.\n"
            f"{'Fuß':<15}Fußbus\n"
            f"{'MIV':<15}Auto, Transporter etc.\n"
            f"{'MIV-Mitfahrer':<15}Mitfahrten, Taxifahrten etc.\n"
            f"{'Sonstiges':<15}Schiff, Flugzeug, Rakete etc.\n"
            f"{'ÖV':<15}Nahverkehr (Bus, Straßenbahn, RB), Fernverkehr (ICE, TGV, Flixtrain, Westbahn, Fernbus) etc.\n"
        )
        body_label = tk.Label(
            table_frame,
            text=body_text,
            font=("Consolas", 10),
            background="white",
            justify="left"
        )
        body_label.pack(anchor="w", padx=5, pady=(0, 5))

    def hide_mode_tooltip(self, event):
        if self.tooltip_window_mode is not None:
            self.tooltip_window_mode.destroy()
            self.tooltip_window_mode = None

    def show_purpose_tooltip(self, event):
        """Zeigt einen Tooltip für Wegezweck."""
        if self.tooltip_window_purpose is not None:
            return
        self.tooltip_window_purpose = tk.Toplevel(self.root)
        self.tooltip_window_purpose.wm_overrideredirect(True)

        x = event.x_root
        y = event.y_root + 20
        self.tooltip_window_purpose.geometry(f"+{x}+{y}")

        table_frame = tk.Frame(self.tooltip_window_purpose, background="white", relief="solid", borderwidth=1)
        table_frame.pack()

        header_label = tk.Label(
            table_frame,
            text=f"{'Wegezweck':<12}{'Hierzu gehören'}",
            font=("Consolas", 10, "bold"),
            background="white",
            justify="left"
        )
        header_label.pack(anchor="w", padx=5, pady=(5, 2))

        body_text = (
            f"{'Arbeit':<12}Wege zur Arbeitsstätte\n"
            f"{'Ausbildung':<12}Wege zur Universität, Schule etc.\n"
            f"{'Begleitung':<12}Kinder zum Kindergarten/zur Schule bringen etc.\n"
            f"{'Dienstlich':<12}Dienstreisen\n"
            f"{'Einkauf':<12}Supermarktbesuche etc.\n"
            f"{'Erledigung':<12}Arztbesuche, Behördengänge etc.\n"
            f"{'Freizeit':<12}Sport, Freunde treffen etc.\n\n"
            "Wege zurück nach Hause zählen zu Freizeit!"
        )
        body_label = tk.Label(
            table_frame,
            text=body_text,
            font=("Consolas", 10),
            background="white",
            justify="left"
        )
        body_label.pack(anchor="w", padx=5, pady=(0, 5))

    def hide_purpose_tooltip(self, event):
        if self.tooltip_window_purpose is not None:
            self.tooltip_window_purpose.destroy()
            self.tooltip_window_purpose = None

    # ---------------------------------------------------------------------------
    #                     Datum- und Uhrzeitauswahl
    # ---------------------------------------------------------------------------
    def select_start_date(self):
        self.select_date(self.start_date_var, "Startdatum")

    def select_end_date(self):
        self.select_date(self.end_date_var, "Enddatum")

    def select_date(self, variable, title):
        """Allgemeiner Kalenderdialog für Datumsauswahl."""
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
        """Allgemeiner Dialog zum Eingeben einer Uhrzeit (HH:MM)."""
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
        ttk.Button(time_frame, text="OK", command=confirm_time).grid(row=1, column=0, columnspan=5, pady=8)
        hour_entry.focus()

    # ---------------------------------------------------------------------------
    #                         Kartenfunktionen
    # ---------------------------------------------------------------------------
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
        """
        Öffnet eine Karte, um Koordinaten (Marker) festzulegen.
        var_name: "start_point" oder "end_point"
        """
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
                handle_error("Es ist bereits ein Marker vorhanden. Bitte zurücksetzen.", self.message_label)
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
            f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/"
            f"{{z}}/{{x}}/{{y}}?access_token={MAPBOX_API_KEY}",
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
                handle_error("Es ist bereits ein Marker vorhanden. Bitte zurücksetzen.", self.message_label)
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

        reset_btn = ttk.Button(
            action_frame,
            text="Marker zurücksetzen",
            command=reset_marker,
            style="BigButton.TButton"
        )
        reset_btn.pack(side=tk.LEFT, padx=10)

        confirm_btn = ttk.Button(
            action_frame,
            text=confirm_btn_text,
            command=confirm_selection,
            style="BigButton.TButton"
        )
        confirm_btn.pack(side=tk.RIGHT, padx=10)

        map_widget.pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------------------------------
    #                    Speichern und Zurücksetzen
    # ---------------------------------------------------------------------------
    def save_entry(self):
        """
        Liest alle Eingabefelder aus, berechnet Distanz und speichert den Eintrag in einer CSV-Datei.
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

        start_datetime_str = f"{start_date} {start_time}"
        end_datetime_str = f"{end_date} {end_time}"

        try:
            start_dt = datetime.strptime(start_datetime_str, "%d.%m.%Y %H:%M")
            end_dt = datetime.strptime(end_datetime_str, "%d.%m.%Y %H:%M")
        except ValueError:
            handle_error("Datum/Zeit-Format ungültig (TT.MM.YYYY HH:MM).", self.message_label)
            return

        if end_dt < start_dt:
            handle_error(
                "Enddatum/-zeit liegt vor Startdatum/-zeit. "
                "Bei Folgetagen bitte das Datum entsprechend anpassen.",
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
        """Setzt die Eingabefelder zurück."""
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
        """Löscht die Meldung im Label (wird bei Änderung eines Feldes aufgerufen)."""
        self.message_label.config(text="")

    def reset_all(self):
        """
        Setzt alle Eingabefelder zurück und löscht die User-/Daten-CSV-Dateien.
        Alle Dateien im CHART_DIRECTORY werden ebenfalls gelöscht.
        """
        self.user_menu.set("")
        if os.path.exists(USER_FILE):
            os.remove(USER_FILE)
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        if os.path.exists(CHART_DIRECTORY):
            for filename in os.listdir(CHART_DIRECTORY):
                file_path = os.path.join(CHART_DIRECTORY, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
        self.load_users()
        self.clear_fields()
        self.message_label.config(text="")
