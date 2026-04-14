import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.parse
import json
import threading
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIG  –  paste your key here
# ─────────────────────────────────────────────
API_KEY = "674bed22167b88b3b69ad8f5f99ce9e5"
BASE_URL = "https://api.openweathermap.org/data/2.5/"

# ─────────────────────────────────────────────
#  WINDOW DIMENSIONS
# ─────────────────────────────────────────────
WIN_W      = 960
WIN_H      = 540
LEFT_W     = 340   # left panel width
RIGHT_W    = WIN_W - LEFT_W   # 620

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
WEATHER_ICONS = {
    "clear":        "☀",
    "clouds":       "☁",
    "rain":         "🌧",
    "drizzle":      "🌦",
    "thunderstorm": "⛈",
    "snow":         "❄",
    "mist":         "🌫",
    "fog":          "🌫",
    "haze":         "🌫",
    "smoke":        "🌫",
    "dust":         "🌫",
    "sand":         "🌫",
    "ash":          "🌋",
    "squall":       "💨",
    "tornado":      "🌪",
}

# (left_top, left_bot, right_bg, card_bg, dim_text, bright_text, accent)
BG_THEMES = {
    "clear":        ("#FFB830", "#FF6B35", "#2B1A00", "#3D2800", "#BF8C30", "#FFFFFF", "#FFD93D"),
    "clouds":       ("#7A9BB0", "#4A6070", "#1A2530", "#243040", "#5A7080", "#FFFFFF", "#A8CEDD"),
    "rain":         ("#2A4F85", "#162840", "#0D1B30", "#162440", "#2A4060", "#FFFFFF", "#5B9BD5"),
    "drizzle":      ("#3A6F98", "#1E4060", "#0E2030", "#182C40", "#305570", "#FFFFFF", "#6BAED6"),
    "thunderstorm": ("#1A1A40", "#0A0A20", "#080818", "#10101E", "#252545", "#FFFFFF", "#8080FF"),
    "snow":         ("#8BB8D4", "#5A90B8", "#1A2A38", "#243040", "#4A7090", "#FFFFFF", "#C9E8F5"),
    "default":      ("#1A2A4E", "#0D1830", "#0A1020", "#121828", "#2A3560", "#FFFFFF", "#4A7FCC"),
}

def get_theme(condition: str):
    key = condition.lower()
    for k, v in BG_THEMES.items():
        if k in key:
            return v
    return BG_THEMES["default"]

def get_weather_icon(condition: str) -> str:
    key = condition.lower()
    for k, v in WEATHER_ICONS.items():
        if k in key:
            return v
    return "🌈"

def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())

def compass(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(deg / 45) % 8]

def blend_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

# ─────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Atmos – Weather")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)

        self._theme  = BG_THEMES["default"]
        self.configure(bg=self._theme[2])
        self._build_ui()

    # ─────────────────────────────────────────
    #  BUILD UI
    # ─────────────────────────────────────────

    def _build_ui(self):
        lt, lb, rbg, card, dim, bright, accent = self._theme

        # ── Left gradient canvas ──────────────
        self.left_canvas = tk.Canvas(self, width=LEFT_W, height=WIN_H,
                                     highlightthickness=0, bd=0)
        self.left_canvas.place(x=0, y=0)
        self._draw_left_gradient(lt, lb)

        # ── Right panel background ────────────
        self.right_canvas = tk.Canvas(self, width=RIGHT_W, height=WIN_H,
                                      highlightthickness=0, bd=0, bg=rbg)
        self.right_canvas.place(x=LEFT_W, y=0)

        # Vertical separator line
        self.right_canvas.create_line(0, 20, 0, WIN_H - 20,
                                      fill=dim, width=1, tags="sep")

        # ══════════════════════════════════════
        #  LEFT PANEL  –  main weather display
        # ══════════════════════════════════════

        # Status / loading text
        self.status_lbl = tk.Label(self, text="Search a city →",
                                   font=("Georgia", 10, "italic"),
                                   fg=dim, bg=lt)
        self.status_lbl.place(x=0, y=14, width=LEFT_W)

        # Big weather icon
        self.icon_lbl = tk.Label(self, text="",
                                  font=("Segoe UI Emoji", 64),
                                  fg=bright, bg=lt)
        self.icon_lbl.place(x=0, y=40, width=LEFT_W)

        # Temperature
        self.temp_lbl = tk.Label(self, text="",
                                  font=("Georgia", 48, "bold"),
                                  fg=bright, bg=lt)
        self.temp_lbl.place(x=0, y=155, width=LEFT_W)

        # Feels like
        self.feels_lbl = tk.Label(self, text="", font=("Georgia", 12),
                                   fg=bright, bg=lt)
        self.feels_lbl.place(x=0, y=238, width=LEFT_W)

        # Description
        self.desc_lbl = tk.Label(self, text="",
                                  font=("Georgia", 16, "italic"),
                                  fg=accent, bg=lt)
        self.desc_lbl.place(x=0, y=265, width=LEFT_W)

        # Location
        self.loc_lbl = tk.Label(self, text="", font=("Georgia", 13),
                                 fg=bright, bg=lt)
        self.loc_lbl.place(x=0, y=298, width=LEFT_W)

        # ── Unit toggle (bottom-left) ─────────
        self.unit_var = tk.StringVar(value="metric")
        self.toggle_frame = tk.Frame(self, bg=lb)
        self.toggle_frame.place(x=10, y=WIN_H - 46, width=LEFT_W - 10)

        self.units_label = tk.Label(self.toggle_frame, text="Units:",
                                    font=("Georgia", 10),
                                    fg=dim, bg=lb)
        self.units_label.pack(side="left")

        self._radio_buttons = []
        for txt, val in [("°C", "metric"), ("°F", "imperial"), ("K", "standard")]:
            rb = tk.Radiobutton(self.toggle_frame, text=txt,
                                variable=self.unit_var, value=val,
                                font=("Georgia", 10),
                                fg=bright, bg=lb,
                                selectcolor=lb,
                                activebackground=lb,
                                activeforeground=accent,
                                command=self._on_unit_change)
            rb.pack(side="left", padx=6)
            self._radio_buttons.append(rb)

        # ══════════════════════════════════════
        #  RIGHT PANEL  –  search + details + forecast
        # ══════════════════════════════════════

        RX = LEFT_W  # right panel x-origin

        # ── Search bar ───────────────────────
        self.search_frame = tk.Frame(self, bg=card, bd=0)
        self.search_frame.place(x=RX + 16, y=16, width=RIGHT_W - 32, height=44)

        self.search_var = tk.StringVar()
        self.entry = tk.Entry(self.search_frame, textvariable=self.search_var,
                              bg=card, fg=dim,
                              insertbackground=bright,
                              font=("Georgia", 13, "italic"),
                              bd=0, relief="flat", highlightthickness=0)
        self.entry.pack(side="left", fill="both", expand=True, padx=14, pady=6)
        self.entry.bind("<Return>", lambda e: self._start_fetch())

        # ── Placeholder behaviour ──
        self._placeholder    = "Enter A City Here"
        self._placeholder_on = True
        self.entry.insert(0, self._placeholder)

        def _on_focus_in(e):
            if self._placeholder_on:
                self.entry.delete(0, "end")
                self.entry.config(fg=bright, font=("Georgia", 13))
                self._placeholder_on = False

        def _on_focus_out(e):
            if not self.entry.get().strip():
                self._placeholder_on = True
                self.entry.config(fg=dim, font=("Georgia", 13, "italic"))
                self.entry.delete(0, "end")
                self.entry.insert(0, self._placeholder)

        self.entry.bind("<FocusIn>",  _on_focus_in)
        self.entry.bind("<FocusOut>", _on_focus_out)

        self.search_btn = tk.Button(self.search_frame, text="⌕",
                                    font=("Georgia", 15, "bold"),
                                    fg=accent, bg=card,
                                    activebackground=dim,
                                    activeforeground=accent,
                                    bd=0, relief="flat", cursor="hand2",
                                    command=self._start_fetch)
        self.search_btn.pack(side="right", padx=10)

        # search border on right canvas
        self.right_canvas.create_rectangle(16, 16, RIGHT_W - 16, 60,
                                           outline=dim, width=1,
                                           tags="search_border")

        # ── Section title: Details ────────────
        self.detail_title = tk.Label(self, text="",
                                      font=("Georgia", 10, "bold"),
                                      fg=dim, bg=rbg)
        self.detail_title.place(x=RX + 16, y=70, width=RIGHT_W - 32)

        # ── Detail cards grid ─────────────────
        self._detail_frame = tk.Frame(self, bg=rbg)
        self._detail_frame.place(x=RX + 16, y=92, width=RIGHT_W - 32, height=174)

        # ── Section title: Forecast ───────────
        self.fc_title = tk.Label(self, text="",
                                  font=("Georgia", 10, "bold"),
                                  fg=dim, bg=rbg)
        self.fc_title.place(x=RX + 16, y=274, width=RIGHT_W - 32)

        # ── Forecast strip ────────────────────
        self.fc_frame = tk.Frame(self, bg=rbg)
        self.fc_frame.place(x=RX + 8, y=294, width=RIGHT_W - 16, height=220)

        # ── Last updated label ────────────────
        self.updated_lbl = tk.Label(self, text="",
                                     font=("Georgia", 9, "italic"),
                                     fg=dim, bg=rbg)
        self.updated_lbl.place(x=RX + 16, y=WIN_H - 26, width=RIGHT_W - 32)

    # ─────────────────────────────────────────
    #  GRADIENT
    # ─────────────────────────────────────────

    def _draw_left_gradient(self, c1: str, c2: str):
        self.left_canvas.delete("bg")
        for i in range(WIN_H):
            color = blend_color(c1, c2, i / WIN_H)
            self.left_canvas.create_line(0, i, LEFT_W, i,
                                         fill=color, tags="bg")
        self.left_canvas.tag_lower("bg")

    # ─────────────────────────────────────────
    #  THEME
    # ─────────────────────────────────────────

    def _apply_theme(self, theme):
        lt, lb, rbg, card, dim, bright, accent = theme
        self._theme = theme

        self.configure(bg=rbg)
        self._draw_left_gradient(lt, lb)

        # Right canvas bg
        self.right_canvas.config(bg=rbg)
        self.right_canvas.delete("sep")
        self.right_canvas.create_line(0, 20, 0, WIN_H - 20,
                                      fill=dim, width=1, tags="sep")
        self.right_canvas.delete("search_border")
        self.right_canvas.create_rectangle(16, 16, RIGHT_W - 16, 60,
                                           outline=dim, width=1,
                                           tags="search_border")

        # Left panel widgets — use mid gradient color as bg proxy
        mid = blend_color(lt, lb, 0.5)
        for w in (self.status_lbl, self.icon_lbl, self.temp_lbl,
                  self.feels_lbl, self.desc_lbl, self.loc_lbl):
            w.config(bg=mid)
        self.status_lbl.config(fg=dim)
        self.icon_lbl.config(fg=bright)
        self.temp_lbl.config(fg=bright)
        self.feels_lbl.config(fg=bright)
        self.desc_lbl.config(fg=accent)
        self.loc_lbl.config(fg=bright)

        # Toggle row
        self.toggle_frame.config(bg=lb)
        self.units_label.config(bg=lb, fg=dim)
        for rb in self._radio_buttons:
            rb.config(bg=lb, fg=bright, selectcolor=lb,
                      activebackground=lb, activeforeground=accent)

        # Right panel widgets
        for w in (self.detail_title, self._detail_frame,
                  self.fc_title, self.fc_frame,
                  self.updated_lbl):
            w.config(bg=rbg)
        self.detail_title.config(fg=dim)
        self.fc_title.config(fg=dim)
        self.updated_lbl.config(fg=dim)

        # Search bar
        self.search_frame.config(bg=card)
        entry_fg = dim if self._placeholder_on else bright
        entry_font = ("Georgia", 13, "italic") if self._placeholder_on else ("Georgia", 13)
        self.entry.config(bg=card, fg=entry_fg, font=entry_font,
                          insertbackground=bright)
        self.search_btn.config(bg=card, fg=accent, activebackground=dim)

    # ─────────────────────────────────────────
    #  FETCH
    # ─────────────────────────────────────────

    def _start_fetch(self):
        raw  = self.entry.get().strip()
        city = "" if (self._placeholder_on or raw == self._placeholder) else raw
        if not city:
            messagebox.showwarning("Atmos", "Please enter a city name.")
            return
        self._set_status("Fetching…")
        self._clear_display()
        threading.Thread(target=self._fetch_weather, args=(city,),
                         daemon=True).start()

    def _on_unit_change(self):
        if self.search_var.get().strip():
            self._start_fetch()

    def _fetch_weather(self, city: str):
        unit   = self.unit_var.get()
        enc    = urllib.parse.quote(city)
        url    = f"{BASE_URL}weather?q={enc}&appid={API_KEY}&units={unit}"
        fc_url = f"{BASE_URL}forecast?q={enc}&appid={API_KEY}&units={unit}&cnt=40"
        try:
            data    = fetch_json(url)
            fc_data = fetch_json(fc_url)
        except urllib.error.HTTPError as e:
            msg = {401: "❌ Invalid API key",
                   404: f"❌ City '{city}' not found"}.get(
                       e.code, f"❌ HTTP {e.code}")
            self.after(0, self._set_status, msg)
            return
        except Exception as ex:
            self.after(0, self._set_status, f"❌ {ex}")
            return
        self.after(0, self._render, data, fc_data, unit)

    # ─────────────────────────────────────────
    #  RENDER
    # ─────────────────────────────────────────

    def _render(self, data: dict, fc_data: dict, unit: str):
        condition  = data["weather"][0]["main"]
        desc       = data["weather"][0]["description"].title()
        temp       = data["main"]["temp"]
        feels      = data["main"]["feels_like"]
        humidity   = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        wind_dir   = compass(data["wind"].get("deg", 0))
        pressure   = data["main"]["pressure"]
        visibility = data.get("visibility", 0) / 1000
        city_name  = data["name"]
        country    = data["sys"]["country"]
        sunrise    = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
        sunset     = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

        unit_sym = {"metric": "°C", "imperial": "°F", "standard": "K"}[unit]
        spd_sym  = {"metric": "m/s", "imperial": "mph", "standard": "m/s"}[unit]

        theme = get_theme(condition)
        self._apply_theme(theme)
        lt, lb, rbg, card, dim, bright, accent = theme
        mid = blend_color(lt, lb, 0.5)

        # ── Left panel ──
        self.icon_lbl.config(text=get_weather_icon(condition), bg=mid)
        self.temp_lbl.config(text=f"{temp:.0f}{unit_sym}", bg=mid)
        self.feels_lbl.config(text=f"Feels like  {feels:.0f}{unit_sym}", bg=mid)
        self.desc_lbl.config(text=desc, bg=mid)
        self.loc_lbl.config(text=f"📍  {city_name}, {country}", bg=mid)
        self._set_status("")

        # ── Detail cards (3×2 grid) ───────────
        self.detail_title.config(text="CURRENT CONDITIONS")
        for w in self._detail_frame.winfo_children():
            w.destroy()

        details = [
            ("💧", "Humidity",   f"{humidity}%"),
            ("🌬", "Wind",       f"{wind_speed} {spd_sym} {wind_dir}"),
            ("🌡", "Pressure",   f"{pressure} hPa"),
            ("👁", "Visibility", f"{visibility:.1f} km"),
            ("🌅", "Sunrise",    sunrise),
            ("🌇", "Sunset",     sunset),
        ]
        for i, (icon, label, val) in enumerate(details):
            col = i % 3
            row = i // 3
            cf = tk.Frame(self._detail_frame, bg=card,
                          highlightbackground=dim, highlightthickness=1)
            cf.grid(row=row, column=col, padx=5, pady=5,
                    ipadx=10, ipady=6, sticky="nsew")
            self._detail_frame.columnconfigure(col, weight=1)
            # icon + label on one line
            tk.Label(cf, text=f"{icon}  {label}",
                     font=("Georgia", 9), fg=dim, bg=card,
                     anchor="w").pack(fill="x", padx=4)
            tk.Label(cf, text=val,
                     font=("Georgia", 13, "bold"),
                     fg=bright, bg=card,
                     anchor="w").pack(fill="x", padx=4)

        # ── 5-Day Forecast ────────────────────
        self.fc_title.config(text="5 - DAY  FORECAST")
        for w in self.fc_frame.winfo_children():
            w.destroy()

        seen_days: dict = {}
        for item in fc_data["list"]:
            day = datetime.fromtimestamp(item["dt"]).strftime("%a")
            if day not in seen_days:
                seen_days[day] = item
            if len(seen_days) == 5:
                break

        for i, (day, item) in enumerate(seen_days.items()):
            fc_cond  = item["weather"][0]["main"]
            fc_desc  = item["weather"][0]["description"].title()
            fc_icon  = get_weather_icon(fc_cond)
            fc_temp  = item["main"]["temp"]
            fc_hum   = item["main"]["humidity"]

            cf = tk.Frame(self.fc_frame, bg=card,
                          highlightbackground=dim, highlightthickness=1)
            cf.grid(row=0, column=i, padx=5, pady=4,
                    ipadx=8, ipady=8, sticky="nsew")
            self.fc_frame.columnconfigure(i, weight=1)

            tk.Label(cf, text=day,
                     font=("Georgia", 11, "bold"),
                     fg=bright, bg=card).pack(pady=(4, 0))
            tk.Label(cf, text=fc_icon,
                     font=("Segoe UI Emoji", 22),
                     fg=bright, bg=card).pack()
            tk.Label(cf, text=f"{fc_temp:.0f}{unit_sym}",
                     font=("Georgia", 12, "bold"),
                     fg=accent, bg=card).pack()
            tk.Label(cf, text=fc_desc,
                     font=("Georgia", 8, "italic"),
                     fg=dim, bg=card, wraplength=80).pack(pady=(0, 2))
            tk.Label(cf, text=f"💧 {fc_hum}%",
                     font=("Georgia", 8),
                     fg=dim, bg=card).pack(pady=(0, 4))

        # ── Last updated ──────────────────────
        now = datetime.now().strftime("%d %b %Y  %H:%M")
        self.updated_lbl.config(text=f"Last updated: {now}")

    # ─────────────────────────────────────────
    #  UTILS
    # ─────────────────────────────────────────

    def _set_status(self, msg: str):
        self.status_lbl.config(text=msg if msg else "Search a city →")

    def _clear_display(self):
        self.icon_lbl.config(text="")
        self.temp_lbl.config(text="")
        self.feels_lbl.config(text="")
        self.desc_lbl.config(text="")
        self.loc_lbl.config(text="")
        self.detail_title.config(text="")
        self.fc_title.config(text="")
        self.updated_lbl.config(text="")
        for w in self._detail_frame.winfo_children():
            w.destroy()
        for w in self.fc_frame.winfo_children():
            w.destroy()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()