# Evolusi Mobil — Remotion Short

Video vertikal 1080×1920, 30 detik, 60 FPS, dengan objek mobil 3D (React Three Fiber) di dalam Remotion 4.

## Struktur

- `src/index.ts`: entry point, mendaftarkan root Remotion
- `src/root.tsx`: mendaftarkan composition `VideoShort`
- `src/video/VideoShort.tsx`: urutan 4 scene (masing-masing 7,5 detik)
- `src/video/Scene.tsx`: lingkungan 3D, kamera, pencahayaan, mobil, dan overlay teks
- `remotion.config.ts`: pengaturan codec, kualitas, dan renderer WebGL
- `.github/workflows/render-video.yml`: render otomatis di GitHub Actions

## Menjalankan di GitHub

1. Buat repository baru, upload seluruh isi folder ini (pastikan `package.json` ada di root repository).
2. Buka tab **Actions** → **Render Video** → **Run workflow**. Workflow juga berjalan otomatis setiap push ke `main`.
3. Setelah selesai, unduh `video-1080x1920-60fps` dari bagian **Artifacts**.

## Mengubah isi

- Teks dan warna setiap scene: edit array `SCENES` di `src/video/VideoShort.tsx`.
- Bentuk dan gerakan mobil: edit komponen `Car` di `src/video/Scene.tsx`.
- Gerakan kamera: edit komponen `Camera` di `src/video/Scene.tsx`.

## Render lokal (opsional)

```bash
npm install
npm start        # Remotion Studio untuk preview
npm run render   # menghasilkan out/video.mp4
```
