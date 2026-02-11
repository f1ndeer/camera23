import cv2
import numpy as np
import time
import winsound
import ctypes
import os
import yt_dlp

# --- АВТОМАТИЧНИЙ ПОШУК VLC ---
vlc_found = False
possible_vlc_paths = [
    r"C:\Program Files\VideoLAN\VLC",
    r"C:\Program Files (x86)\VideoLAN\VLC"
]

# Шукаємо папку VLC
for path in possible_vlc_paths:
    if os.path.exists(path):
        os.add_dll_directory(path) # Для Python 3.8+
        os.environ['PATH'] = path + ";" + os.environ['PATH']
        vlc_found = True
        print(f"[OK] VLC found: {path}") # Прибрав емодзі
        break

if not vlc_found:
    print("[ERROR] VLC Player not found!") # Прибрав емодзі
    print("Please install VLC Player (64-bit).")
    exit()

import vlc # Імпортуємо тільки після налаштування шляхів

# --- НАЛАШТУВАННЯ ---
FIXED_WIDTH = 1280
FIXED_HEIGHT = 720
MOTION_THRESHOLD = 50000 
DELAY_SECONDS = 2        

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']

# --- ЗВУК СИСТЕМИ ---
def set_system_volume(volume_level):
    converted_volume = int(volume_level * 655.35)
    hex_volume = (converted_volume << 11) | converted_volume
    ctypes.windll.winmm.waveOutSetVolume(0, hex_volume)

def stop_music_force():
    winsound.PlaySound(None, winsound.SND_PURGE)

# --- YOUTUBE ---
def get_youtube_stream_url(youtube_url):
    print(f"YouTube processing: {youtube_url} ...")
    ydl_opts = {'format': 'best', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info['url']
    except Exception as e:
        print(f"YouTube Error: {e}")
        return None

file_paths = [
    'image_left.jpg', 
    'vlad.jpg',
    'image_right.jpg', 
    'rondaldo.mp4',
    'https://www.youtube.com/watch?v=AlnHNi0hdO0', 
    'https://www.youtube.com/watch?v=AlnHNi0hdO0', 
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 
    'image_top.jpg', 
    'image_bottom.jpg',
    'image_45.jpg',
    'image_21.jpg',
    'image_211.jpg',
    'image_32.jpg',
    'image_3333.jpg',
    'image_4444.jpg',
    'andrey.jpg',
    'images.webp'
]

# Завантаження медіа
media_list = []
print("Loading media...")

for path in file_paths:
    # 1. YouTube (Використовуємо VLC для звука)
    if path.startswith('http://') or path.startswith('https://'):
        stream_url = get_youtube_stream_url(path)
        if stream_url:
            media_list.append({
                'type': 'youtube', # Спеціальний тип для YouTube
                'path': path,
                'stream_url': stream_url
            })
            print(f"YouTube OK (VLC): {path}")
            
    # 2. Локальні файли (Використовуємо OpenCV - без звука)
    else:
        ext = os.path.splitext(path)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            cap_vid = cv2.VideoCapture(path)
            if cap_vid.isOpened():
                media_list.append({
                    'type': 'video_silent', # Тип для локальних відео
                    'data': cap_vid, 
                    'path': path
                })
                print(f"Local Video OK (Silent): {path}")
        else:
            # Картинки
            img = cv2.imread(path)
            if img is not None:
                img = cv2.resize(img, (FIXED_WIDTH, FIXED_HEIGHT))
                media_list.append({'type': 'image', 'data': img, 'path': path})
                print(f"Image OK: {path}")

def center_window(window_name, width, height):
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    cv2.moveWindow(window_name, x, y)

# --- ОСНОВНИЙ ЦИКЛ ---
cap = cv2.VideoCapture(0)
ret, frame1 = cap.read()
if not ret: exit()

prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
prvs = cv2.GaussianBlur(prvs, (21, 21), 0)

current_media_index = 0
window_open = False
last_motion_time = 0
music_playing = False


vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

while True:
    ret, frame2 = cap.read()
    if not ret: break

    next_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    next_frame = cv2.GaussianBlur(next_frame, (21, 21), 0)
    diff = cv2.absdiff(prvs, next_frame)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    motion_level = np.sum(thresh)
    current_time = time.time()

    if motion_level > MOTION_THRESHOLD:
        # --- Є РУХ ---
        last_motion_time = current_time 
        
        if not window_open:
            current_media_index = (current_media_index + 1) % len(media_list)
            current_item = media_list[current_media_index]
            
            window_open = True
            
            window_name = 'Motion Media'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, FIXED_WIDTH, FIXED_HEIGHT)
            center_window(window_name, FIXED_WIDTH, FIXED_HEIGHT)
            
            # --- ЛОГІКА ЗАПУСКУ ---
            
            # ВАРІАНТ 1: YouTube (VLC зі звуком)
            if current_item['type'] == 'youtube':
                stop_music_force()
                music_playing = False
                
                # Прив'язуємо VLC до вікна OpenCV
                hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
                if hwnd: player.set_hwnd(hwnd)
                
                media = vlc_instance.media_new(current_item['stream_url'])
                media.add_option('input-repeat=65535') 
                player.set_media(media)
                player.play()
                print(f"YouTube Start: {current_item['path']}")

            # ВАРІАНТ 2: Локальне відео (OpenCV без звука)
            elif current_item['type'] == 'video_silent':
                if player.is_playing(): player.stop()
                stop_music_force()
                music_playing = False
                
                # Скидання відео на початок
                current_item['data'].set(cv2.CAP_PROP_POS_FRAMES, 0)
                print(f"Local Video Start: {current_item['path']}")

            # ВАРІАНТ 3: Картинка (Звук сирени)
            else:
                if player.is_playing(): player.stop()
                if not music_playing:
                    try:
                        set_system_volume(2)
                        winsound.PlaySound('alert.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                        music_playing = True
                    except: pass
                print(f"Image Start: {current_item['path']}")

        # --- ВІДОБРАЖЕННЯ ---
        current_item = media_list[current_media_index]
        
        if current_item['type'] == 'youtube':
            # VLC малює сам, просто чекаємо
            cv2.waitKey(1)
            
        elif current_item['type'] == 'video_silent':
            # Читаємо кадр локального відео
            vid_cap = current_item['data']
            ret_vid, vid_frame = vid_cap.read()
            
            if not ret_vid: # Зациклення
                vid_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_vid, vid_frame = vid_cap.read()
            
            if ret_vid:
                vid_frame = cv2.resize(vid_frame, (FIXED_WIDTH, FIXED_HEIGHT))
                if window_open: cv2.imshow('Motion Media', vid_frame)
        
        elif current_item['type'] == 'image':
            if window_open: cv2.imshow('Motion Media', current_item['data'])

        cv2.putText(frame2, "STATUS: MOTION DETECTED", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    
    else:
        # --- НЕМАЄ РУХУ ---
        if window_open and (current_time - last_motion_time > DELAY_SECONDS):
            # Зупиняємо все
            if player.is_playing(): player.stop()
            if music_playing: stop_music_force(); music_playing = False
            
            cv2.destroyWindow('Motion Media') 
            window_open = False
        
        if window_open:
            remaining = int(DELAY_SECONDS - (current_time - last_motion_time))
            cv2.putText(frame2, f"Closing: {remaining}s", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            # Продовжуємо відтворення, поки йде таймер
            current_item = media_list[current_media_index]
            
            if current_item['type'] == 'video_silent':
                vid_cap = current_item['data']
                ret_vid, vid_frame = vid_cap.read()
                if not ret_vid:
                    vid_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret_vid, vid_frame = vid_cap.read()
                if ret_vid:
                    vid_frame = cv2.resize(vid_frame, (FIXED_WIDTH, FIXED_HEIGHT))
                    cv2.imshow('Motion Media', vid_frame)
            
            elif current_item['type'] == 'image':
                 cv2.imshow('Motion Media', current_item['data'])
            # YouTube (VLC) грає сам

        else:
            cv2.putText(frame2, "STATUS: WAITING", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # Гарантована зупинка
            if player.is_playing(): player.stop()
            if music_playing: stop_music_force(); music_playing = False

    cv2.imshow('Camera Feed', frame2)
    prvs = next_frame
    
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

player.stop()
cap.release()
cv2.destroyAllWindows()