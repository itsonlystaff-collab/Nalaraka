# Render Video 1080x1920

Project ini merender video vertikal (1080×1920, 30 fps, MP4) dari voiceover dan naskah teks, lalu berjalan otomatis di GitHub Actions.

## Isi

- `voiceover.mp3`: audio narasi (panjang menentukan durasi video)
- `naskah.json`: judul, brand, dan teks per segmen
- `scripts/build.py`: script render
- `.github/workflows/render.yml`: workflow GitHub Actions

## Cara pakai di GitHub

1. Buat repository baru di GitHub, lalu upload seluruh isi folder ini.
2. Push ke branch `main`. Workflow akan berjalan otomatis.
3. Atau buka tab **Actions**, pilih **Render Video 1080x1920**, lalu klik **Run workflow**.
4. Setelah selesai, unduh hasilnya dari bagian **Artifacts**: `video-1080x1920`.

## Mengubah isi video

- **Ganti teks:** edit `naskah.json`. Durasi tiap segmen dihitung otomatis dari jumlah kata.
- **Ganti audio:** timpa `voiceover.mp3` dengan file baru.
- **Ganti judul dan brand:** ubah field `title` dan `brand` di `naskah.json`.

## Render lokal (opsional)

Butuh Python 3, Pillow, dan FFmpeg.

```bash
pip install pillow
python scripts/build.py
```

Hasil ada di `output/video.mp4`.

## Catatan

Timing teks per segmen diperkirakan dari jumlah kata, belum disinkronkan per kata dengan audio. Jika teks di `naskah.json` tidak persis sama dengan isi voiceover, sesuaikan teksnya agar pas dengan narasi.
