import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {ThreeCanvas} from '@remotion/three';

export type SceneConfig = {
  id: string;
  year: string;
  title: string;
  caption: string;
  background: string;
  fog: string;
  ground: string;
  road: string;
  bodyColor: string;
  trimColor: string;
  wheelColor: string;
  wheelRadius: number;
  bodyLength: number;
  bodyWidth: number;
  bodyHeight: number;
  cabinHeight: number;
  spokes: boolean;
  glow: boolean;
  accent: string;
  lightIntensity: number;
  orbitStart: number;
};

type SceneProps = {
  config: SceneConfig;
  index: number;
  total: number;
  duration: number;
};

/* ----------------------------- Lingkungan ----------------------------- */

const Environment: React.FC<{config: SceneConfig; frame: number}> = ({
  config,
  frame,
}) => {
  const period = 39;
  const speed = 0.12;
  const dashes = Array.from({length: 13}, (_, i) => {
    return ((i * 3 + frame * speed) % period) - period / 2;
  });

  return (
    <>
      <color attach="background" args={[config.background]} />
      <fog attach="fog" args={[config.fog, 12, 30]} />

      {/* Tanah */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[90, 90]} />
        <meshStandardMaterial color={config.ground} roughness={1} />
      </mesh>

      {/* Jalan */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.005, 0]}>
        <planeGeometry args={[90, 5]} />
        <meshStandardMaterial color={config.road} roughness={0.9} />
      </mesh>

      {/* Garis putus-putus yang bergerak, memberi kesan mobil melaju */}
      {dashes.map((x, i) => (
        <mesh key={`dash-${i}`} position={[x, 0.012, 0]}>
          <boxGeometry args={[1.4, 0.01, 0.08]} />
          <meshStandardMaterial
            color="#f5f5f5"
            emissive="#ffffff"
            emissiveIntensity={0.15}
          />
        </mesh>
      ))}
    </>
  );
};

/* ------------------------------ Pencahayaan --------------------------- */

const Lights: React.FC<{config: SceneConfig; frame: number}> = ({
  config,
  frame,
}) => {
  const angle = frame * 0.02;
  return (
    <>
      <ambientLight intensity={0.35} />
      <directionalLight position={[5, 8, 6]} intensity={1.1} color="#ffffff" />
      <directionalLight
        position={[-6, 3, -4]}
        intensity={0.4}
        color={config.accent}
      />
      <pointLight
        position={[Math.cos(angle) * 4.5, 2.5, Math.sin(angle) * 4.5]}
        intensity={config.lightIntensity}
        color={config.accent}
        distance={18}
      />
    </>
  );
};

/* -------------------------------- Kamera ------------------------------ */

const Camera: React.FC<{config: SceneConfig; frame: number; duration: number}> =
  ({config, frame, duration}) => {
    const progress = interpolate(frame, [0, duration], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    });

    const angle = ((config.orbitStart + progress * 70) * Math.PI) / 180;
    const radius = 9.2 - progress * 1.8;
    const height = 1.7 + Math.sin(frame * 0.025) * 0.25;
    const position: [number, number, number] = [
      Math.cos(angle) * radius,
      height,
      Math.sin(angle) * radius,
    ];

    return (
      <perspectiveCamera
        makeDefault
        fov={36}
        near={0.1}
        far={200}
        position={position}
        onUpdate={(cam) => cam.lookAt(0, 1.1, 0)}
      />
    );
  };

/* ---------------------------------- Mobil ----------------------------- */

const Car: React.FC<{config: SceneConfig; frame: number; fps: number}> = ({
  config: c,
  frame,
  fps,
}) => {
  // Mobil meluncur turun ke posisinya di awal scene
  const entrance = spring({
    frame: frame - 4,
    fps,
    config: {damping: 16, stiffness: 110, mass: 1},
  });
  const drop = interpolate(entrance, [0, 1], [3, 0]);

  // Gerakan halus: bobbing dan sedikit goyangan
  const bob = Math.sin(frame * 0.09) * 0.02;
  const sway = Math.sin(frame * 0.05) * 0.012;

  // Putaran roda
  const spin = frame * 0.2;

  const R = c.wheelRadius;
  const tire = R * 0.22;
  const hubY = R + tire; // pusat roda; sisi bawah ban tepat di y = 0
  const L = c.bodyLength;
  const W = c.bodyWidth;
  const H = c.bodyHeight;
  const CH = c.cabinHeight;
  const axleX = L * 0.3;
  const axleZ = W / 2 + tire * 0.6;

  const renderWheel = (x: number, z: number, key: string) => (
    <group key={key} position={[x, hubY, z]}>
      <group rotation={[0, 0, spin]}>
        {/* Ban */}
        <mesh>
          <torusGeometry args={[R, tire, 14, 40]} />
          <meshStandardMaterial color={c.wheelColor} roughness={0.9} />
        </mesh>
        {/* Velg */}
        <mesh>
          <torusGeometry args={[R * 0.7, tire * 0.35, 10, 36]} />
          <meshStandardMaterial
            color={c.trimColor}
            metalness={0.7}
            roughness={0.3}
          />
        </mesh>
        {c.spokes ? (
          Array.from({length: 6}, (_, i) => (
            <mesh key={`spoke-${i}`} rotation={[0, 0, (i * Math.PI) / 3]}>
              <boxGeometry args={[R * 1.4, R * 0.1, R * 0.1]} />
              <meshStandardMaterial
                color={c.trimColor}
                metalness={0.7}
                roughness={0.3}
              />
            </mesh>
          ))
        ) : (
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[R * 0.7, R * 0.7, tire * 0.4, 32]} />
            <meshStandardMaterial
              color={c.trimColor}
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
        )}
        {/* Hub */}
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[R * 0.18, R * 0.18, tire * 1.2, 20]} />
          <meshStandardMaterial
            color={c.trimColor}
            metalness={0.8}
            roughness={0.25}
          />
        </mesh>
      </group>
    </group>
  );

  return (
    <>
      {/* Bayangan kontak di tanah; makin tipis saat mobil masih melayang */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.01, 0]}
        scale={[L * 0.62, W * 2.2, 1]}
      >
        <circleGeometry args={[1, 48]} />
        <meshBasicMaterial
          color="#000000"
          transparent
          opacity={Math.max(0.12, 0.45 - drop * 0.12)}
        />
      </mesh>

      <group position={[0, drop + bob, 0]} rotation={[0, 0, sway]}>
        {/* Badan utama */}
        <mesh position={[0, hubY + H / 2, 0]}>
          <boxGeometry args={[L, H, W]} />
          <meshStandardMaterial
            color={c.bodyColor}
            metalness={0.35}
            roughness={0.42}
          />
        </mesh>

        {/* Kabin */}
        <mesh position={[-L * 0.08, hubY + H + CH / 2, 0]}>
          <boxGeometry args={[L * 0.5, CH, W * 0.88]} />
          <meshStandardMaterial
            color={c.bodyColor}
            metalness={0.35}
            roughness={0.42}
          />
        </mesh>

        {/* Grill depan */}
        <mesh position={[L / 2 + 0.02, hubY + H * 0.45, 0]}>
          <boxGeometry args={[0.06, H * 0.5, W * 0.8]} />
          <meshStandardMaterial
            color={c.trimColor}
            metalness={0.8}
            roughness={0.25}
          />
        </mesh>

        {/* Lampu depan */}
        {[-1, 1].map((side) => (
          <mesh
            key={`head-${side}`}
            position={[L / 2 + 0.04, hubY + H * 0.7, side * W * 0.3]}
          >
            <sphereGeometry args={[0.07, 16, 16]} />
            <meshStandardMaterial
              color="#fff6d5"
              emissive={c.accent}
              emissiveIntensity={c.glow ? 2.2 : 0.8}
            />
          </mesh>
        ))}

        {/* Garis cahaya di bawah bodi (mobil listrik) */}
        {c.glow && (
          <mesh position={[0, hubY - 0.03, 0]}>
            <boxGeometry args={[L * 0.95, 0.04, W * 1.02]} />
            <meshStandardMaterial
              color={c.accent}
              emissive={c.accent}
              emissiveIntensity={2}
            />
          </mesh>
        )}

        {/* Empat roda */}
        {[-1, 1].map((sx) =>
          [-1, 1].map((sz) =>
            renderWheel(sx * axleX, hubY, sz * axleZ, `wheel-${sx}-${sz}`)
          )
        )}
      </group>
    </>
  );
};

/* -------------------------------- Scene ------------------------------- */

export const Scene: React.FC<SceneProps> = ({
  config,
  index,
  total,
  duration,
}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();

  const titleIn = spring({frame: frame - 10, fps, config: {damping: 200}});
  const captionIn = spring({frame: frame - 26, fps, config: {damping: 200}});

  const fadeIn = interpolate(frame, [0, 14], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(frame, [duration - 14, duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const overlayOpacity = Math.max(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{backgroundColor: config.background}}>
      {/* Layer 3D */}
      <AbsoluteFill>
        <ThreeCanvas width={width} height={height}>
          <Environment config={config} frame={frame} />
          <Lights config={config} frame={frame} />
          <Camera config={config} frame={frame} duration={duration} />
          <Car config={config} frame={frame} fps={fps} />
        </ThreeCanvas>
      </AbsoluteFill>

      {/* Layer teks */}
      <AbsoluteFill
        style={{
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '160px 80px 200px',
          color: '#ffffff',
          fontFamily: 'Arial, Helvetica, sans-serif',
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            textAlign: 'center',
            opacity: titleIn,
            transform: `translateY(${interpolate(titleIn, [0, 1], [50, 0])}px)`,
          }}
        >
          <div
            style={{
              fontSize: 190,
              fontWeight: 900,
              lineHeight: 1,
              color: config.accent,
            }}
          >
            {config.year}
          </div>
          <div style={{fontSize: 70, fontWeight: 800, marginTop: 10}}>
            {config.title}
          </div>
        </div>

        <div
          style={{
            textAlign: 'center',
            maxWidth: 880,
            opacity: captionIn,
            transform: `translateY(${interpolate(captionIn, [0, 1], [40, 0])}px)`,
          }}
        >
          <div style={{fontSize: 44, lineHeight: 1.35, fontWeight: 500}}>
            {config.caption}
          </div>
          <div
            style={{
              display: 'flex',
              gap: 14,
              justifyContent: 'center',
              marginTop: 50,
            }}
          >
            {Array.from({length: total}, (_, i) => (
              <div
                key={`dot-${i}`}
                style={{
                  width: i === index ? 56 : 16,
                  height: 16,
                  borderRadius: 8,
                  backgroundColor:
                    i === index ? config.accent : 'rgba(255,255,255,0.35)',
                }}
              />
            ))}
          </div>
        </div>
      </AbsoluteFill>

      {/* Transisi hitam di awal dan akhir scene */}
      <AbsoluteFill style={{backgroundColor: '#000000', opacity: overlayOpacity}} />
    </AbsoluteFill>
  );
};
