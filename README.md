# Jakarta Low-Poly 3D Animation — GitHub Actions Render Pipeline

Proyek animasi 3D bergaya **Low-Poly Stylized Cinematic** dengan **ekspresi wajah karakter** (kedipan mata alami, pergerakan alis ekspresif, serta animasi mulut tersenyum/berbicara/menghirup udara segar), resolusi portrait **1080×1920 @ 30 FPS**, berdurasi **75 detik (2.250 frame)** yang disinkronkan penuh dengan audio narasi.

## Spesifikasi Teknis
- **Resolusi & Frame Rate:** `1080×1920` (9:16 Portrait), `30 FPS` Constant Frame Rate (`H.264` + `AAC 48kHz`).
- **Durasi Audio Voiceover:** `72,12 detik` (`assets/audio/voiceover.mp3`).
- **Durasi Total Video:** `75 detik` (`1,0 detik` pembuka + `72,12 detik` narasi + `1,88 detik` penutup dengan *audio fade-out* 2,5 detik).
- **Jumlah Scene:** 10 scene terpisah dengan lokasi, objek bergerak independen (MRT, KRL, bus TransJakarta, sepeda, karakter berjalan/duduk), dan pergerakan kamera sinematik.

## Cara Menjalankan Render di GitHub Actions
1. Ekstrak seluruh isi file `.zip` ini dan unggah (*push*) ke repositori GitHub Anda.
2. Buka tab **Actions** pada repositori GitHub Anda.
3. Pilih workflow **Render Jakarta Low-Poly 3D Animation (1080x1920)**.
4. Klik tombol **Run workflow** (Anda dapat memilih engine `BLENDER_EEVEE_NEXT` untuk render cepat ±15–25 menit atau `CYCLES` untuk kualitas pencahayaan ray-traced).
5. Setelah proses selesai, unduh hasil video MP4 final beserta gambar pratinjau Quality Control pada bagian **Artifacts** (`jakarta-lowpoly-3d-1080x1920`).
