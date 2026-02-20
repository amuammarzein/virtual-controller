import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
import time

# -------------------------
# Config / inisialisasi
# -------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands_detector = mp_hands.Hands(
    max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.5
)

keyboard = Controller()

# Mapping gesture -> key(s)
MAP = {
    "Maju": [],
    "Mundur": [],
    "Belok Kiri": [Key.left],
    "Belok Kanan": [Key.right],
    "Rem": [Key.space],
    "Kombo 1": ["d"],
    "Kombo 2": ["s"],
    "NOS": ["a"],
    "Diam": [],
    "Menunggu": [],
}

pressed_keys = set()


# -------------------------
# Fungsi util
# -------------------------
def count_open_fingers(landmarks, tol=0.02):
    if not landmarks:
        return 0
    count = 0
    finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky
    for tip in finger_tips:
        if landmarks[tip].y < (landmarks[tip - 2].y - tol):
            count += 1
    return count


def get_palm_center(landmarks):
    if not landmarks:
        return None, None
    x_center = (landmarks[5].x + landmarks[17].x) / 2
    y_center = (landmarks[5].y + landmarks[17].y) / 2
    return x_center, y_center


def decide_gesture(hand_landmarks_list, hand_labels):

    # Dua tangan
    info = list(zip(hand_landmarks_list, hand_labels))
    right_hand = next((lm for lm, lbl in info if lbl == "Right"), None)
    left_hand = next((lm for lm, lbl in info if lbl == "Left"), None)

    open_right = count_open_fingers(right_hand) if right_hand else 0
    open_left = count_open_fingers(left_hand) if left_hand else 0

    if right_hand and left_hand:
        x_r, y_r = get_palm_center(right_hand)
        x_l, y_l = get_palm_center(left_hand)
        if x_r is None or x_l is None:
            return "Menunggu"

        if open_left >= 1 and open_right >= 1:
            return "Rem"

        if open_right >= 2 and open_left < 1:
            return "Kombo 2"

        if open_right >= 1 and open_left < 1:
            return "Kombo 1"

        if open_left >= 1 and open_right < 1:
            return "NOS"

        if open_left == 0 and open_right == 0:
            slope = (y_r - y_l) / (x_r - x_l + 1e-6)
            TH_SLOPE = 0.5
            if abs(slope) <= TH_SLOPE:
                return "Maju"
            elif slope > TH_SLOPE:
                return "Belok Kanan"
            elif slope < -TH_SLOPE:
                return "Belok Kiri"

        return "Menunggu"

    return "Menunggu"


def update_keyboard(pressed_set, gesture):
    desired = set(MAP.get(gesture, []))
    # Release keys not desired anymore
    for k in list(pressed_set):
        if k not in desired:
            try:
                keyboard.release(k)
            except Exception:
                pass
            pressed_set.discard(k)
    # Press new keys
    for k in desired:
        if k not in pressed_set:
            try:
                keyboard.press(k)
            except Exception:
                pass
            pressed_set.add(k)


# -------------------------
# Main loop
# -------------------------
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Gagal membuka kamera.")
    exit(1)

time.sleep(0.5)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    H, W, _ = frame.shape

    # Proses tangan di frame penuh
    results = hands_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    hands = []
    labels = []
    if results.multi_hand_landmarks:
        for lm, handed in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
            hands.append(lm.landmark)
            labels.append(handed.classification[0].label)

    # Deteksi gesture
    gesture = decide_gesture(hands, labels)

    # Kirim keyboard sesuai gesture
    update_keyboard(pressed_keys, gesture)

    # Tampilkan label gesture
    font = cv2.FONT_HERSHEY_DUPLEX
    text = f"Gesture: {gesture}"
    (tw, th), _ = cv2.getTextSize(text, font, 1, 1)

    pad_x = 10
    pad_y = 20

    x1 = frame.shape[1] - (pad_x + tw + pad_x)  # posisi kiri kotak
    y1 = 5  # posisi atas kotak

    # Gambar kotak background dengan padding lebih tinggi
    cv2.rectangle(
        frame, (x1, y1), (x1 + tw + pad_x * 2, y1 + th + pad_y), (0, 0, 0), -1
    )

    # Gambar teks di dalam kotak dengan padding kiri dan atas
    cv2.putText(
        frame,
        text,
        (x1 + pad_x, y1 + th + (pad_y // 2)),
        font,
        1,
        (0, 255, 0),
        1,
        cv2.LINE_AA,
    )

    print(text)
    cv2.imshow("1P Driving (gesture -> keyboard)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC untuk keluar
        break

# Lepaskan semua tombol saat keluar
for k in list(pressed_keys):
    try:
        keyboard.release(k)
    except:
        pass

cap.release()
cv2.destroyAllWindows()
