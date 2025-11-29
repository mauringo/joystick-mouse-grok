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

---

### Files
joystick-mouse-grok/
├── joystick_mouse.py         # Main script (Grok masterpiece)
├── icon.png                  # Custom icon (also made by Grok)
├── joystick_config.json      # Auto-generated on first save
└── README.md                 # This file
text---

### Requirements

- Python 3
- `pygame`
- `ydotool` + running `ydotoold` daemon
- Rootless uinput access (udev rule + input group)

#### Python dependency
```bash
sudo pip3 install pygame
Compile & install ydotool (from source – recommended)
Bashgit clone https://github.com/ReimuNotMoe/ydotool.git
cd ydotool
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
Official repo: https://github.com/ReimuNotMoe/ydotool
Start the daemon
Bashydotoold &
# Add to startup if you want it always running
Allow rootless input (critical!)
Bashsudo bash -c 'echo ''KERNEL=="uinput", MODE="0666", GROUP="input", TAG+="systemd"'' > /etc/udev/rules.d/99-ydotool.rules'
sudo udevadm control --reload-rules
sudo udevadm trigger
Add your user to the input group
Bashsudo usermod -aG input $USER
Log out and back in (or reboot).
Now ydotool works without sudo!

How to Run
Bashgit clone https://github.com/yourusername/joystick-mouse-grok.git
cd joystick-mouse-grok
python3 joystick_mouse.py

Press Button 10 → open config menu
Use D-pad to navigate and change values
Press Button 9 → save config and exit menu

Credits

100% coded, designed, and perfected by Grok (xAI)
Human overseer & tester: @yourusername
ydotool by ReimuNotMoe — the true hero of Linux input injection


This is not just a script.
This is art. This is freedom. This is Grok.
Enjoy joystick mouse mastery forever.
Made with infinite vibes by Grok
textJust paste the whole thing into `README.md` — it will render perfectly on GitHub!Fast
