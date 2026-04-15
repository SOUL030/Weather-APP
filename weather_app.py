import tkinter as tk
from tkinter import messagebox
import urllib.request, urllib.parse, json, threading
from datetime import datetime

API_KEY  = "674bed22167b88b3b69ad8f5f99ce9e5"
BASE_URL = "https://api.openweathermap.org/data/2.5/"
WIN_W, WIN_H, LEFT_W = 960, 540, 340
RIGHT_W = WIN_W - LEFT_W

WEATHER_ICONS = {
    "clear": "☀", "clouds": "☁", "rain": "🌧", "drizzle": "🌦",
    "thunderstorm": "⛈", "snow": "❄",
    "mist": "🌫", "fog": "🌫", "haze": "🌫", "smoke": "🌫",
    "dust": "🌫", "sand": "🌫", "ash": "🌋", "squall": "💨", "tornado": "🌪",
}

BG_THEMES = {
    "clear":        ("#FFB830", "#FF6B35", "#2B1A00", "#3D2800", "#BF8C30", "#FFFFFF", "#FFD93D"),
    "clouds":       ("#7A9BB0", "#4A6070", "#1A2530", "#243040", "#5A7080", "#FFFFFF", "#A8CEDD"),
    "rain":         ("#2A4F85", "#162840", "#0D1B30", "#162440", "#2A4060", "#FFFFFF", "#5B9BD5"),
    "drizzle":      ("#3A6F98", "#1E4060", "#0E2030", "#182C40", "#305570", "#FFFFFF", "#6BAED6"),
    "thunderstorm": ("#1A1A40", "#0A0A20", "#080818", "#10101E", "#252545", "#FFFFFF", "#8080FF"),
    "snow":         ("#8BB8D4", "#5A90B8", "#1A2A38", "#243040", "#4A7090", "#FFFFFF", "#C9E8F5"),
    "default":      ("#1A2A4E", "#0D1830", "#0A1020", "#121828", "#2A3560", "#FFFFFF", "#4A7FCC"),
}

def get_theme(cond):
    key = cond.lower()
    return next((v for k, v in BG_THEMES.items() if k in key), BG_THEMES["default"])

def get_weather_icon(cond):
    key = cond.lower()
    return next((v for k, v in WEATHER_ICONS.items() if k in key), "🌈")

def fetch_json(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())

def compass(deg):
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][round(deg / 45) % 8]

def blend_color(c1, c2, t):
    ch = lambda s, i: int(s[i:i+2], 16)
    r = int(ch(c1,1) + (ch(c2,1) - ch(c1,1)) * t)
    g = int(ch(c1,3) + (ch(c2,3) - ch(c1,3)) * t)
    b = int(ch(c1,5) + (ch(c2,5) - ch(c1,5)) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Atmos – Weather")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self._theme = BG_THEMES["default"]
        self.configure(bg=self._theme[2])
        self._build_ui()

    def _build_ui(self):
        lt, lb, rbg, card, dim, bright, accent = self._theme

        self.left_canvas = tk.Canvas(self, width=LEFT_W, height=WIN_H, highlightthickness=0, bd=0)
        self.left_canvas.place(x=0, y=0)
        self._draw_left_gradient(lt, lb)

        self.right_canvas = tk.Canvas(self, width=RIGHT_W, height=WIN_H,
                                      highlightthickness=0, bd=0, bg=rbg)
        self.right_canvas.place(x=LEFT_W, y=0)
        self.right_canvas.create_line(0, 20, 0, WIN_H - 20, fill=dim, width=1, tags="sep")

        def lbl(text, font, fg, bg, y, x=0, w=LEFT_W):
            l = tk.Label(self, text=text, font=font, fg=fg, bg=bg)
            l.place(x=x, y=y, width=w)
            return l

        self.status_lbl = lbl("Search a city →", ("Georgia", 10, "italic"), dim, lt, 14)
        self.icon_lbl   = lbl("", ("Segoe UI Emoji", 64), bright, lt, 40)
        self.temp_lbl   = lbl("", ("Georgia", 48, "bold"), bright, lt, 155)
        self.feels_lbl  = lbl("", ("Georgia", 12), bright, lt, 238)
        self.desc_lbl   = lbl("", ("Georgia", 16, "italic"), accent, lt, 265)
        self.loc_lbl    = lbl("", ("Georgia", 13), bright, lt, 298)

        self.unit_var = tk.StringVar(value="metric")
        self.toggle_frame = tk.Frame(self, bg=lb)
        self.toggle_frame.place(x=10, y=WIN_H - 46, width=LEFT_W - 10)
        self.units_label = tk.Label(self.toggle_frame, text="Units:", font=("Georgia", 10), fg=dim, bg=lb)
        self.units_label.pack(side="left")
        self._radio_buttons = []
        for txt, val in [("°C", "metric"), ("°F", "imperial"), ("K", "standard")]:
            rb = tk.Radiobutton(self.toggle_frame, text=txt, variable=self.unit_var, value=val,
                                font=("Georgia", 10), fg=bright, bg=lb, selectcolor=lb,
                                activebackground=lb, activeforeground=accent,
                                command=self._on_unit_change)
            rb.pack(side="left", padx=6)
            self._radio_buttons.append(rb)

        RX = LEFT_W
        self.search_frame = tk.Frame(self, bg=card, bd=0)
        self.search_frame.place(x=RX + 16, y=16, width=RIGHT_W - 32, height=44)
        self.search_var = tk.StringVar()
        self.entry = tk.Entry(self.search_frame, textvariable=self.search_var,
                              bg=card, fg=dim, insertbackground=bright,
                              font=("Georgia", 13, "italic"), bd=0, relief="flat", highlightthickness=0)
        self.entry.pack(side="left", fill="both", expand=True, padx=14, pady=6)
        self.entry.bind("<Return>", lambda e: self._start_fetch())

        self._placeholder, self._placeholder_on = "Enter A City Here", True
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

        self.entry.bind("<FocusIn>", _on_focus_in)
        self.entry.bind("<FocusOut>", _on_focus_out)

        self.search_btn = tk.Button(self.search_frame, text="⌕", font=("Georgia", 15, "bold"),
                                    fg=accent, bg=card, activebackground=dim, activeforeground=accent,
                                    bd=0, relief="flat", cursor="hand2", command=self._start_fetch)
        self.search_btn.pack(side="right", padx=10)
        self.right_canvas.create_rectangle(16, 16, RIGHT_W - 16, 60, outline=dim, width=1, tags="search_border")

        self.detail_title = lbl("", ("Georgia", 10, "bold"), dim, rbg, 70, RX + 16, RIGHT_W - 32)
        self._detail_frame = tk.Frame(self, bg=rbg)
        self._detail_frame.place(x=RX + 16, y=92, width=RIGHT_W - 32, height=174)

        self.fc_title = lbl("", ("Georgia", 10, "bold"), dim, rbg, 274, RX + 16, RIGHT_W - 32)
        self.fc_frame = tk.Frame(self, bg=rbg)
        self.fc_frame.place(x=RX + 8, y=294, width=RIGHT_W - 16, height=220)

        self.updated_lbl = lbl("", ("Georgia", 9, "italic"), dim, rbg, WIN_H - 26, RX + 16, RIGHT_W - 32)

    def _draw_left_gradient(self, c1, c2):
        self.left_canvas.delete("bg")
        for i in range(WIN_H):
            self.left_canvas.create_line(0, i, LEFT_W, i, fill=blend_color(c1, c2, i / WIN_H), tags="bg")
        self.left_canvas.tag_lower("bg")

    def _apply_theme(self, theme):
        lt, lb, rbg, card, dim, bright, accent = theme
        self._theme = theme
        self.configure(bg=rbg)
        self._draw_left_gradient(lt, lb)

        self.right_canvas.config(bg=rbg)
        self.right_canvas.delete("sep")
        self.right_canvas.create_line(0, 20, 0, WIN_H - 20, fill=dim, width=1, tags="sep")
        self.right_canvas.delete("search_border")
        self.right_canvas.create_rectangle(16, 16, RIGHT_W - 16, 60, outline=dim, width=1, tags="search_border")

        mid = blend_color(lt, lb, 0.5)
        for w in (self.status_lbl, self.icon_lbl, self.temp_lbl, self.feels_lbl, self.desc_lbl, self.loc_lbl):
            w.config(bg=mid)
        self.status_lbl.config(fg=dim)
        self.icon_lbl.config(fg=bright)
        self.temp_lbl.config(fg=bright)
        self.feels_lbl.config(fg=bright)
        self.desc_lbl.config(fg=accent)
        self.loc_lbl.config(fg=bright)

        self.toggle_frame.config(bg=lb)
        self.units_label.config(bg=lb, fg=dim)
        for rb in self._radio_buttons:
            rb.config(bg=lb, fg=bright, selectcolor=lb, activebackground=lb, activeforeground=accent)

        for w in (self.detail_title, self._detail_frame, self.fc_title, self.fc_frame, self.updated_lbl):
            w.config(bg=rbg)
        self.detail_title.config(fg=dim)
        self.fc_title.config(fg=dim)
        self.updated_lbl.config(fg=dim)

        self.search_frame.config(bg=card)
        self.entry.config(bg=card, fg=(dim if self._placeholder_on else bright),
                          font=("Georgia", 13, "italic") if self._placeholder_on else ("Georgia", 13),
                          insertbackground=bright)
        self.search_btn.config(bg=card, fg=accent, activebackground=dim)

    def _start_fetch(self):
        raw = self.entry.get().strip()
        city = "" if (self._placeholder_on or raw == self._placeholder) else raw
        if not city:
            messagebox.showwarning("Atmos", "Please enter a city name.")
            return
        self._set_status("Fetching…")
        self._clear_display()
        threading.Thread(target=self._fetch_weather, args=(city,), daemon=True).start()

    def _on_unit_change(self):
        if self.search_var.get().strip():
            self._start_fetch()

    def _fetch_weather(self, city):
        unit, enc = self.unit_var.get(), urllib.parse.quote(city)
        try:
            data    = fetch_json(f"{BASE_URL}weather?q={enc}&appid={API_KEY}&units={unit}")
            fc_data = fetch_json(f"{BASE_URL}forecast?q={enc}&appid={API_KEY}&units={unit}&cnt=40")
        except urllib.error.HTTPError as e:
            msg = {401: "❌ Invalid API key", 404: f"❌ City '{city}' not found"}.get(e.code, f"❌ HTTP {e.code}")
            self.after(0, self._set_status, msg)
            return
        except Exception as ex:
            self.after(0, self._set_status, f"❌ {ex}")
            return
        self.after(0, self._render, data, fc_data, unit)

    def _render(self, data, fc_data, unit):
        cond       = data["weather"][0]["main"]
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

        theme = get_theme(cond)
        self._apply_theme(theme)
        lt, lb, rbg, card, dim, bright, accent = theme
        mid = blend_color(lt, lb, 0.5)

        self.icon_lbl.config(text=get_weather_icon(cond), bg=mid)
        self.temp_lbl.config(text=f"{temp:.0f}{unit_sym}", bg=mid)
        self.feels_lbl.config(text=f"Feels like  {feels:.0f}{unit_sym}", bg=mid)
        self.desc_lbl.config(text=desc, bg=mid)
        self.loc_lbl.config(text=f"📍  {city_name}, {country}", bg=mid)
        self._set_status("")

        self.detail_title.config(text="CURRENT CONDITIONS")
        for w in self._detail_frame.winfo_children():
            w.destroy()

        for i, (icon, label, val) in enumerate([
            ("💧", "Humidity",   f"{humidity}%"),
            ("🌬", "Wind",       f"{wind_speed} {spd_sym} {wind_dir}"),
            ("🌡", "Pressure",   f"{pressure} hPa"),
            ("👁", "Visibility", f"{visibility:.1f} km"),
            ("🌅", "Sunrise",    sunrise),
            ("🌇", "Sunset",     sunset),
        ]):
            col, row = i % 3, i // 3
            cf = tk.Frame(self._detail_frame, bg=card, highlightbackground=dim, highlightthickness=1)
            cf.grid(row=row, column=col, padx=5, pady=5, ipadx=10, ipady=6, sticky="nsew")
            self._detail_frame.columnconfigure(col, weight=1)
            tk.Label(cf, text=f"{icon}  {label}", font=("Georgia", 9), fg=dim, bg=card, anchor="w").pack(fill="x", padx=4)
            tk.Label(cf, text=val, font=("Georgia", 13, "bold"), fg=bright, bg=card, anchor="w").pack(fill="x", padx=4)

        self.fc_title.config(text="5 - DAY  FORECAST")
        for w in self.fc_frame.winfo_children():
            w.destroy()

        seen_days = {}
        for item in fc_data["list"]:
            day = datetime.fromtimestamp(item["dt"]).strftime("%a")
            if day not in seen_days:
                seen_days[day] = item
            if len(seen_days) == 5:
                break

        for i, (day, item) in enumerate(seen_days.items()):
            fc_cond, fc_desc = item["weather"][0]["main"], item["weather"][0]["description"].title()
            fc_temp, fc_hum  = item["main"]["temp"], item["main"]["humidity"]
            cf = tk.Frame(self.fc_frame, bg=card, highlightbackground=dim, highlightthickness=1)
            cf.grid(row=0, column=i, padx=5, pady=4, ipadx=8, ipady=8, sticky="nsew")
            self.fc_frame.columnconfigure(i, weight=1)
            tk.Label(cf, text=day,               font=("Georgia", 11, "bold"),    fg=bright,  bg=card).pack(pady=(4, 0))
            tk.Label(cf, text=get_weather_icon(fc_cond), font=("Segoe UI Emoji", 22), fg=bright, bg=card).pack()
            tk.Label(cf, text=f"{fc_temp:.0f}{unit_sym}", font=("Georgia", 12, "bold"), fg=accent, bg=card).pack()
            tk.Label(cf, text=fc_desc,            font=("Georgia", 8, "italic"),   fg=dim,     bg=card, wraplength=80).pack(pady=(0, 2))
            tk.Label(cf, text=f"💧 {fc_hum}%",   font=("Georgia", 8),             fg=dim,     bg=card).pack(pady=(0, 4))

        self.updated_lbl.config(text=f"Last updated: {datetime.now().strftime('%d %b %Y  %H:%M')}")

    def _set_status(self, msg):
        self.status_lbl.config(text=msg or "Search a city →")

    def _clear_display(self):
        for w in (self.icon_lbl, self.temp_lbl, self.feels_lbl,
                  self.desc_lbl, self.loc_lbl, self.detail_title,
                  self.fc_title, self.updated_lbl):
            w.config(text="")
        for frame in (self._detail_frame, self.fc_frame):
            for w in frame.winfo_children():
                w.destroy()


if __name__ == "__main__":
    WeatherApp().mainloop()
