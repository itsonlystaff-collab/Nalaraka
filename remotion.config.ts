import {Config} from '@remotion/cli/config';

// Format output
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setCrf(18);
Config.setOverwriteOutput(true);

// Renderer WebGL untuk React Three Fiber di server Linux tanpa GPU (GitHub Actions).
// Jika render gagal dengan error WebGL, ganti nilai ini menjadi 'swiftshader'.
Config.setChromiumOpenGlRenderer('swangle');
