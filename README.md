# 🏎️ Gesture Steering Control

Kontrol game balapan menggunakan gerakan tangan via Webcam (Python + MediaPipe).

## 🚀 Quick Start
1. **Instal Library:**
   pip install opencv-python mediapipe pynput
   
2. **Run Script:**
   python nama_file_kamu.py

3. **Keluar:** Tekan tombol `ESC` pada jendela kamera.

## 🎮 Kontrol & Gesture
Program menghitung kemiringan tangan dan jumlah jari untuk input keyboard:



| Kondisi Tangan | Aksi | Tombol |
| :--- | :--- | :--- |
| **Miring Kiri/Kanan** | Stir | `←` / `→` |
| **Dua Tangan Terbuka** | Rem | `Space` |
| **Tangan Kiri Terbuka** | NOS | `A` |
| **Tangan Kanan (1 Jari)** | Kombo 1 | `D` |
| **Tangan Kanan (2+ Jari)** | Kombo 2 | `S` |

## 🛠️ Tips & Troubleshooting
* **Kamera:** Jika kamera tidak muncul, ubah `cv2.VideoCapture(1)` menjadi `0` di bagian akhir script.
* **Game:** Jika input tidak masuk ke dalam game, jalankan Terminal/VS Code sebagai **Administrator**.
* **Pencahayaan:** Pastikan ruangan terang agar titik tangan (*landmarks*) terdeteksi stabil.

---
*Dibuat dengan Python, OpenCV, dan MediaPipe.*