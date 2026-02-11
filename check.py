import sys
import os

print("\n--- ДИАГНОСТИКА НАЧАЛАСЬ ---")
print(f"Версия Python: {sys.version}")

try:
    import mediapipe
    print(f"Откуда грузится MediaPipe: {mediapipe.__file__}")
    
    if hasattr(mediapipe, 'solutions'):
        print("СТАТУС: Библиотека работает! (solutions найден)")
    else:
        print("СТАТУС: ОШИБКА! Библиотека пустая (solutions НЕ найден)")
        print("Содержимое модуля:", dir(mediapipe))

except ImportError:
    print("СТАТУС: MediaPipe вообще не установлен.")
except Exception as e:
    print(f"Другая ошибка: {e}")

print("\nФайлы в папке:")
print(os.listdir())
print("--- ДИАГНОСТИКА ЗАКОНЧЕНА ---\n")