# 🌤 Atmos — Python Weather App

A sleek, desktop weather application built with **Python + Tkinter** that fetches real-time weather data from the **OpenWeatherMap API**. Features a dynamic gradient UI that changes color based on current weather conditions.

---

## 📸 Preview

```
┌──────────────────────────────────────────────────────────────────┐
│  LEFT PANEL (340px)          │  RIGHT PANEL (620px)              │
│  ─────────────────────────── │  ────────────────────────────── │
│                               │  [ Search city...           ⌕ ] │
│         ☀                    │                                   │
│        32°C                  │  CURRENT CONDITIONS               │
│   Feels like 30°C            │  💧 Humidity  🌬 Wind  🌡 Pressure│
│      Clear Sky               │   13%       4m/s W   1008 hPa    │
│    📍 Dehradun, IN           │  👁 Visibil  🌅 Sunrise 🌇 Sunset │
│                               │   10.0 km    05:52     18:43    │
│  ─────────────────────────── │                                   │
│  Units: ●°C  ○°F  ○K        │  5-DAY FORECAST                   │
│                               │  Tue  Wed  Thu  Fri  Sat        │
│                               │  ☀    ☀    ☁    🌧   ☁          │
│                               │  32°  20°  21°  23°  24°        │
│                               │  Clear  Clear  Clouds Rain ...  │
└──────────────────────────────────────────────────────────────────┘┘
```

---

##  Features

-  **Current Temperature** with "feels like" reading
-  **Weather Description** and animated condition icon
-  **City & Country** display
-  **Humidity, Pressure, Visibility**
-  **Wind Speed & Compass Direction**
-  **Sunrise & Sunset** times
- **5-Day Forecast** strip
-  **Dynamic Gradient Background** — changes with weather condition
- **Unit Toggle** — switch between °C, °F, and Kelvin instantly
-  **Threaded API calls** — UI stays responsive while fetching
-  **Error Handling** — friendly messages for bad keys, unknown cities, network failures

---

## 🛠 Requirements

| Requirement | Version |
|---|---|
| Python | 3.6 or higher |
| tkinter | Included with Python (see below) |
| OpenWeatherMap API Key | Free tier works |

> **No pip installs needed** — this app uses only Python's standard library.

### Linux Users
If `tkinter` is not installed, run:
```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora / RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

---

##  Quick Start

### Step 1 — Get a Free API Key
1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click **Sign Up** and create a free account
3. Navigate to **My API Keys** and copy your key
4. Note: New keys may take up to 10 minutes to activate

### Step 2 — Configure the App
Open `weather_app.py` in any text editor and replace line 12:
```python
# Before
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

# After
API_KEY = "a1b2c3d4e5f6789abcdef1234567890"  # your actual key
```

### Step 3 — Run

**Windows (double-click):**
```
run_weather_app.bat
```

**Windows (command line):**
```cmd
python weather_app.py
```

**macOS / Linux:**
```bash
python3 weather_app.py
```

---

## 📁 Project Structure

```
atmos-weather-app/
│
├── weather_app.py        # Main application source
├── requirements.txt      # Dependency notes (stdlib only)
├── run_weather_app.bat   # Windows one-click launcher
└── README.md             # This file
```

---

## 🎨 Weather Backgrounds

The background gradient automatically adapts to conditions:

| Condition | Gradient |
|---|---|
| ☀ Clear | Golden yellow → warm orange |
| ☁ Cloudy | Steel blue → slate grey |
| 🌧 Rain | Ocean blue → deep navy |
| ⛈ Thunderstorm | Midnight indigo → near-black |
| ❄ Snow | Pale sky blue → ice blue |
| 🌫 Fog / Mist | Muted blue-grey tones |

---

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| `❌ Invalid API key` | Double-check the key in `weather_app.py`; wait 10 min after creating |
| `❌ City not found` | Try the English name (e.g. `Mumbai` not `मुंबई`) |
| `tkinter not found` | See **Linux Users** section above |
| `Python not found` | Install Python 3.6+ from [python.org](https://python.org) |
| Network error | Check your internet connection |

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

- Weather data: [OpenWeatherMap API](https://openweathermap.org/api)
- Built with Python's built-in `tkinter` GUI toolkit
