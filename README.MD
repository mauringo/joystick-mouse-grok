# Joystick → Mouse (Grok Edition)

**The ultimate joystick-to-mouse controller — 100% vibecoded by Grok**

> A hyper-smooth, physics-based joystick mouse emulator for Linux  
> Works in background • Instant right click • Media keys • Full config menu • Live stats

**Everything in this project was generated, refined, and perfected by Grok (xAI)**  
Yes — every single line of code, every feature, every pixel — 100% AI-vibecoded.

---

### Features

- Ultra-smooth physics-based movement (acceleration + friction + magnitude-based velocity clamping)  
- Background joystick input (works even when window is not focused)  
- Live analog bars for axes 0–3 + real-time pressed buttons display  
- Full in-game config menu (adjust everything with the D-pad)  
- Mute / Play-Pause / Volume / Next-Prev via D-pad and buttons  
- Instant right click (zero lag)  
- Left click & drag hold  
- Saves/loads settings automatically (`joystick_config.json`)  
- Beautiful custom icon  
- Fully portable — only 3 files needed



## Joystick Script Requirements

| Component       | Description                                      | Installation/Notes                          |
|-----------------|--------------------------------------------------|---------------------------------------------|
| Python 3        | Required runtime for script execution            | Pre-installed on most Linux/macOS systems  |
| pygame          | Handles joystick input, GUI display, events      | `pip install pygame` [12]                |
| ydotool         | Simulates mouse/keyboard events (Linux daemon)   | see down |
| Joystick Device | Hardware accessible via pygame joystick API      | OS drivers (Linux: evdev permissions)  |
| joystick_config.json | Settings file (auto-generated)               | Created in script directory on first save  |



## Clone and build ydotool
git clone https://github.com/ReimuNotMoe/ydotool.git
cd ydotool
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install

