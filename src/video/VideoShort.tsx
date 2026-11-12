import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {Scene, SceneConfig} from './Scene';

export const FPS = 60;
export const DURATION_SECONDS = 30;
export const TOTAL_FRAMES = FPS * DURATION_SECONDS; // 1800 frame

const SCENE_COUNT = 4;
export const SCENE_FRAMES = TOTAL_FRAMES / SCENE_COUNT; // 450 frame = 7,5 detik

export const SCENES: SceneConfig[] = [
  {
    id: 'benz-1886',
    year: '1886',
    title: 'Patent-Motorwagen',
    caption:
      'Mobil bermesin bensin pertama yang dipatenkan. Bentuknya masih mirip kereta kuda.',
    background: '#1c1812',
    fog: '#1c1812',
    ground: '#3b3428',
    road: '#2a241b',
    bodyColor: '#8a5a2b',
    trimColor: '#2b2b2b',
    wheelColor: '#1c1c1c',
    wheelRadius: 0.78,
    bodyLength: 2.6,
    bodyWidth: 1.1,
    bodyHeight: 0.5,
    cabinHeight: 0.35,
    spokes: true,
    glow: false,
    accent: '#ffb347',
    lightIntensity: 1.2,
    orbitStart: 20,
  },
  {
    id: 'ford-1908',
    year: '1908',
    title: 'Ford Model T',
    caption:
      'Mobil yang dibuat untuk banyak orang, dengan harga yang makin terjangkau.',
    background: '#0f2420',
    fog: '#0f2420',
    ground: '#1d3a33',
    road: '#15241f',
    bodyColor: '#16161d',
    trimColor: '#c9a227',
    wheelColor: '#141414',
    wheelRadius: 0.7,
    bodyLength: 2.9,
    bodyWidth: 1.3,
    bodyHeight: 0.7,
    cabinHeight: 0.8,
    spokes: true,
    glow: false,
    accent: '#7fd1ae',
    lightIntensity: 1.4,
    orbitStart: 80,
  },
  {
    id: 'chrome-1958',
    year: '1958',
    title: 'Sedan Krom',
    caption:
      'Bodi lebar, krom mengilap, dan sirip belakang menjadi simbol zamannya.',
    background: '#2a0f1f',
    fog: '#2a0f1f',
    ground: '#3d1a2c',
    road: '#24101b',
    bodyColor: '#c0392b',
    trimColor: '#d9d9d9',
    wheelColor: '#111111',
    wheelRadius: 0.5,
    bodyLength: 3.4,
    bodyWidth: 1.5,
    bodyHeight: 0.55,
    cabinHeight: 0.5,
    spokes: false,
    glow: false,
    accent: '#ff6b8a',
    lightIntensity: 1.6,
    orbitStart: 140,
  },
  {
    id: 'ev-2026',
    year: '2026',
    title: 'Mobil Listrik',
    caption:
      'Keselamatan canggih, layar sentuh, dan mesin listrik membuat mobil lebih pintar dan bersih.',
    background: '#06131f',
    fog: '#06131f',
    ground: '#0c2233',
    road: '#081a28',
    bodyColor: '#eaf4ff',
    trimColor: '#1a2a3a',
    wheelColor: '#111111',
    wheelRadius: 0.5,
    bodyLength: 3.2,
    bodyWidth: 1.4,
    bodyHeight: 0.5,
    cabinHeight: 0.45,
    spokes: false,
    glow: true,
    accent: '#3ef0ff',
    lightIntensity: 2,
    orbitStart: 200,
  },
];

export const VideoShort: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#000000'}}>
      {SCENES.map((scene, index) => (
        <Sequence
          key={scene.id}
          from={index * SCENE_FRAMES}
          durationInFrames={SCENE_FRAMES}
          name={scene.id}
        >
          <Scene
            config={scene}
            index={index}
            total={SCENES.length}
            duration={SCENE_FRAMES}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
