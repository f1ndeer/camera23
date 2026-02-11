import cv2
import numpy as np

# 0 — це індекс стандартної веб-камери
cap = cv2.VideoCapture(0)

print("Натисніть 'q', щоб вийти")

while True:
    # Захоплюємо кадр
    ret, frame = cap.read()
    
    if not ret:
        print("Помилка: не вдалося отримати кадр.")
        break

    # Відображаємо результат
    cv2.imshow('Camera Test', frame)

    # Чекаємо натискання клавіші 'q' для виходу
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()