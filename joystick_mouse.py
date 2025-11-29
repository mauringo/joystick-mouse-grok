#!/usr/bin/env python3
"""
YOUR ABSOLUTE FINAL MASTERPIECE
- Loads config at startup (at boot)
- Shows current max_velocity, acceleration, friction in GUI
- Bigger log box — no cutoff
- Analog bars for axes 0-3
- Your exact settings as default
"""

import os
import argparse
import json
import pygame
import sys
import time
import subprocess
import atexit
from pathlib import Path

# Always find files next to script
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / "joystick_config.json"
ICON_FILE   = SCRIPT_DIR / "icon.png"

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

# =============================================================================
# YOUR PERSONAL DEFAULT SETTINGS
# =============================================================================
DEFAULT_PARAMS = {
    "sensitivity": 1.2,
    "deadzone": 0.07,
    "max_velocity": 13.0,
    "friction": 0.6,
    "acceleration": 10.0,

    "screen_width": 900,
    "screen_height": 620,
    "fps": 144,

    "joystick_index": 0,
    "window_title": "Joystick → Mouse (Btn10 = Config)",

    "mouse_x_axis": 0,
    "mouse_y_axis": 1,

    "btn_left_drag": 0,
    "btn_right_click": 1,
    "btn_mute": 2,
    "btn_play_pause": 3,
    "btn_stop_mouse": 6,
    "btn_resume_mouse": 5,

    "hat_up_key": 114,
    "hat_down_key": 115,
    "hat_right_key": 163,
    "hat_left_key": 165,

    "btn_enter_config": 10,
    "btn_save_config": 9,
}

# =============================================================================
# CONFIG MENU – FULLY VISIBLE
# =============================================================================
CONFIG_ITEMS = [
    ("sensitivity",   0.1,  0.1,   7.0, "{:.1f}"),
    ("deadzone",      0.01, 0.0,   0.3, "{:.3f}"),
    ("max_velocity",  1.0,  1.0,  30.0, "{:.0f}"),
    ("friction",      0.1,  0.1,   1.0, "{:.1f}"),
    ("acceleration", 0.1,  1.0,  20.0, "{:.1f}"),
]

# =============================================================================
# LOAD / SAVE
# =============================================================================
def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f), True
        except:
            pass
    return {}, False

def save_config(params):
    saveable = {k: v for k, v in params.items() if k in DEFAULT_PARAMS}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(saveable, f, indent=2)
        return True
    except:
        return False

# =============================================================================
# LOG – BIGGER BOX
# =============================================================================
class LogDisplay:
    def __init__(self):
        self.logs = []
        self.saved_time = 0.0

    def add(self, msg):
        ts = time.strftime("%H:%M")
        short = msg[:56] + "..." if len(msg) > 59 else msg
        self.logs.append(f"[{ts}] {short}")
        if len(self.logs) > 14:
            self.logs.pop(0)

    def render(self, screen):
        # Bigger log box
        pygame.draw.rect(screen, (15,15,25), (15,360,450,220))
        pygame.draw.rect(screen, (100,100,100), (15,360,450,220), 2)
        for i, line in enumerate(self.logs):
            col = (0,255,100) if any(w in line.upper() for w in ["SAVED","MUTE","PLAY"]) else (200,220,255)
            screen.blit(pygame.font.Font(None,17).render(line, True, col), (24, 368 + i*16))
        screen.blit(pygame.font.Font(None,24).render("LOGS", True, (80,255,80)), (24,335))

        if time.time() - self.saved_time < 2.0:
            s = pygame.font.Font(None,72).render("SAVED!", True, (0,255,0))
            screen.blit(s, (450 - s.get_width()//2, 280))

# =============================================================================
# JOYSTICK CLASS
# =============================================================================
class Joy:
    def __init__(self, idx):
        self.idx = idx
        self.j = None
        self.connected = False
        self.name = ""
        self.nbtn = 0

    def init(self):
        if pygame.joystick.get_count() <= self.idx:
            self.connected = False
            return False
        try:
            if not self.j:
                self.j = pygame.joystick.Joystick(self.idx)
            self.j.init()
            self.connected = True
            self.name = self.j.get_name()
            self.nbtn = self.j.get_numbuttons()
            return True
        except:
            self.connected = False
            return False

    def a(self, x):
        return self.j.get_axis(x) if self.connected else 0.0

    def b(self, x):
        return self.j.get_button(x) if self.connected else False

    def h(self):
        return self.j.get_hat(0) if self.connected else (0,0)

# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser()
    for k, v in DEFAULT_PARAMS.items():
        t = type(v)
        if t is bool:
            parser.add_argument(f"--{k}", action="store_true", default=v)
        else:
            parser.add_argument(f"--{k}", type=t, default=v)
    args = parser.parse_args()

    # LOAD CONFIG AT STARTUP (AT BOOT)
    saved_cfg, using_file = load_config()
    for k, v in saved_cfg.items():
        if hasattr(args, k):
            setattr(args, k, v)

    pygame.init()
    pygame.joystick.init()

    if ICON_FILE.exists():
        try:
            pygame.display.set_icon(pygame.image.load(str(ICON_FILE)))
        except:
            pass

    screen = pygame.display.set_mode((args.screen_width, args.screen_height))
    pygame.display.set_caption(args.window_title)
    clock = pygame.time.Clock()

    joy = Joy(args.joystick_index)
    joy.init()

    # Start ydotoold and keep a handle; no blocking wait here
    ydotoold_proc = subprocess.Popen(
        ['ydotoold'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Give it a moment to start
    time.sleep(2.2)

    log = LogDisplay()
    log.add("Ready – Btn10 = Config")

    vx = vy = 0.0
    mouse_active = True
    dragging = False
    config_mode = False
    sel = 0
    prev_hat = (0,0)
    last_hat_time = 0
    btn_state = {}

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        joy.init()
        hat = joy.h()

        def edge(key, btn):
            p = joy.b(btn)
            was = btn_state.get(key, False)
            if p and not was:
                btn_state[key] = True
                return True
            if not p:
                btn_state[key] = False
            return False

        if edge("cfg", args.btn_enter_config):
            config_mode = not config_mode
            log.add("CONFIG MODE" if config_mode else "NORMAL MODE")

        if config_mode:
            now = time.time()
            if hat != prev_hat and now - last_hat_time > 0.18:
                last_hat_time = now
                if hat == (0,1):
                    sel = (sel + 1) % len(CONFIG_ITEMS)
                if hat == (0,-1):
                    sel = (sel - 1) % len(CONFIG_ITEMS)
                if hat in ((1,0), (-1,0)):
                    k, step, mn, mx, _ = CONFIG_ITEMS[sel]
                    val = getattr(args, k)
                    delta = step if hat == (1,0) else -step
                    new_val = max(mn, min(mx, round(val + delta, 2) if step < 1 else val + delta))
                    setattr(args, k, new_val)
                    log.add(f"{k} → {new_val}")

            if edge("save", args.btn_save_config):
                if save_config(vars(args)):
                    log.saved_time = time.time()
                    log.add("SAVED joystick_config.json")
                config_mode = False
        else:
            if edge("stop", args.btn_stop_mouse):
                mouse_active = False
                log.add("MOUSE STOPPED")
            if edge("resume", args.btn_resume_mouse):
                mouse_active = True
                log.add("MOUSE RESUMED")
            if edge("mute", args.btn_mute):
                subprocess.run(['ydotool','key','113:1','113:0'])
                log.add("MUTE")
            if edge("play", args.btn_play_pause):
                subprocess.run(['ydotool','key','164:1','164:0'])
                log.add("PLAY/PAUSE")

            if hat != prev_hat:
                cmds = {(0,-1):114, (0,1):115, (1,0):163, (-1,0):165}
                if hat in cmds:
                    subprocess.run(['ydotool','key',f'{cmds[hat]}:1',f'{cmds[hat]}:0'])

            if mouse_active and joy.connected:
                raw_x = joy.a(args.mouse_x_axis)
                raw_y = joy.a(args.mouse_y_axis)
                if abs(raw_x) < args.deadzone:
                    raw_x = 0
                if abs(raw_y) < args.deadzone:
                    raw_y = 0

                vx += raw_x * args.acceleration
                vy += raw_y * args.acceleration
                vx *= args.friction
                vy *= args.friction

                speed = (vx**2 + vy**2)**0.5
                if speed > args.max_velocity:
                    vx = vx / speed * args.max_velocity
                    vy = vy / speed * args.max_velocity

                dx = int(vx * args.sensitivity)
                dy = int(vy * args.sensitivity)
                if dx or dy:
                    subprocess.run(['ydotool','mousemove',f'-x {dx}',f'-y {dy}'])

                if joy.b(args.btn_right_click):
                    subprocess.run(['ydotool','click','0xC1'])

                if joy.b(args.btn_left_drag) and not dragging:
                    subprocess.run(['ydotool','click','0x40'])
                    dragging = True
                elif not joy.b(args.btn_left_drag) and dragging:
                    subprocess.run(['ydotool','click','0xB0'])
                    dragging = False

        prev_hat = hat

        # ============================= RENDER =============================
        screen.fill((22,22,32))

        cfg_text = f"CONFIG: {'joystick_config.json' if using_file else 'DEFAULT'}"
        cfg_col = (50,255,50) if using_file else (255,180,0)
        screen.blit(pygame.font.Font(None,26).render(cfg_text, True, cfg_col), (20,8))

        screen.blit(pygame.font.Font(None,38).render(
            f"JOYSTICK: {'ON' if joy.connected else 'OFF'}",
            True, (0,255,100) if joy.connected else (255,70,70)), (20,45))
        if joy.connected:
            screen.blit(pygame.font.Font(None,24).render(joy.name[:55], True, (100,255,255)), (20,90))

        screen.blit(pygame.font.Font(None,34).render(
            f"MOUSE: {'ACTIVE' if mouse_active else 'STOPPED'}",
            True, (0,255,0) if mouse_active else (255,100,100)), (20,135))

        pressed = [i for i in range(joy.nbtn) if joy.b(i)]
        btn_txt = "PRESSED: " + (", ".join(map(str, pressed)) if pressed else "none")
        screen.blit(pygame.font.Font(None,30).render(btn_txt, True,
                    (255,255,100) if pressed else (130,130,130)), (20,180))

        if config_mode:
            screen.blit(pygame.font.Font(None,64).render("CONFIG MODE", True, (255,220,0)), (220,80))
            y = 160
            for i, (k, step, mn, mx, fmt) in enumerate(CONFIG_ITEMS):
                val = getattr(args, k)
                col = (255,255,120) if i==sel else (240,240,240)
                pref = "> " if i==sel else "  "
                screen.blit(pygame.font.Font(None,36).render(
                    f"{pref}{k.replace('_',' ').title():14}: {val:.1f}", True, col), (120,y))
                y += 50
        else:
            rx = 480
            speed = (vx**2 + vy**2)**0.5
            screen.blit(pygame.font.Font(None,32).render("CURRENT PARAMS", True, (255,200,100)), (rx,20))
            params = [
                f"Max Vel : {args.max_velocity:.0f}",
                f"Accel   : {args.acceleration:.1f}",
                f"Friction : {args.friction:.1f}",
                f"Speed   : {speed:.1f} ≤ {args.max_velocity:.0f}",
            ]
            for i,t in enumerate(params):
                screen.blit(pygame.font.Font(None,26).render(t, True, (180,255,180)), (rx, 70+i*38))

            # ANALOG BARS FOR AXES 0-3
            screen.blit(pygame.font.Font(None,32).render("ANALOG AXES 0-3", True, (255,200,100)), (rx,220))
            bw = 300
            for i in range(4):
                y = 260 + i * 55
                if joy.connected and joy.j is not None and i < joy.j.get_numaxes():
                    val = joy.a(i)
                else:
                    val = 0.0
                screen.blit(pygame.font.Font(None,24).render(
                    f"Axis {i}: {val:+.3f}", True, (180,255,180)), (rx, y))
                fill = int((val + 1) * bw / 2)
                pygame.draw.rect(screen, (80,80,100), (rx, y+28, bw, 20), 2)
                pygame.draw.rect(screen, (100,200,255), (rx, y+28, fill, 20))

        log.render(screen)
        pygame.display.flip()
        clock.tick(args.fps)

    # Clean up
    pygame.quit()

    # Kill ydotoold without using a blocking run() in atexit
    try:
        # First, try to terminate the process we started
        if ydotoold_proc and ydotoold_proc.poll() is None:
            ydotoold_proc.terminate()
            try:
                ydotoold_proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                ydotoold_proc.kill()

        # As a fallback, also pkill, but without blocking indefinitely
        subprocess.Popen(['sudo', 'pkill', '-f', 'ydotoold'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    except Exception:
        pass

if __name__ == "__main__":
    main()
