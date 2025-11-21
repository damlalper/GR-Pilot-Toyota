import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, Sky } from '@react-three/drei';
import { Suspense, useMemo, useEffect, useRef } from 'react';
import { RacingCar } from './RacingCar';
import { RaceTrack } from './RaceTrack';
import { useStore } from '../store/useStore';
import * as THREE from 'three';

function Scene() {
  const { lapData, currentIndex, isPlaying, playbackSpeed, setCurrentIndex } = useStore();
  const cameraRef = useRef<THREE.PerspectiveCamera>(null);

  const scale = 0.01;

  // Calculate track center for normalization
  const trackCenter = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) return { x: 0, y: 0 };
    const minX = Math.min(...lapData.data.map((p) => p.WorldPositionX));
    const maxX = Math.max(...lapData.data.map((p) => p.WorldPositionX));
    const minY = Math.min(...lapData.data.map((p) => p.WorldPositionY));
    const maxY = Math.max(...lapData.data.map((p) => p.WorldPositionY));
    return { x: (minX + maxX) / 2, y: (minY + maxY) / 2 };
  }, [lapData]);

  // Get current car position and rotation
  const carState = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) {
      return { position: [0, 0, 0] as [number, number, number], rotation: 0, speed: 0 };
    }

    const idx = Math.min(currentIndex, lapData.data.length - 1);
    const current = lapData.data[idx];
    const next = lapData.data[Math.min(idx + 1, lapData.data.length - 1)];

    const x = (current.WorldPositionX - trackCenter.x) * scale;
    const z = (current.WorldPositionY - trackCenter.y) * scale;

    // Calculate rotation based on direction
    const dx = (next.WorldPositionX - current.WorldPositionX) * scale;
    const dz = (next.WorldPositionY - current.WorldPositionY) * scale;
    const rotation = Math.atan2(dx, dz);

    return {
      position: [x, 0, z] as [number, number, number],
      rotation,
      speed: current.speed || 0,
    };
  }, [lapData, currentIndex, trackCenter, scale]);

  // Animation loop
  useEffect(() => {
    if (!isPlaying || !lapData?.data) return;

    const interval = setInterval(() => {
      setCurrentIndex((currentIndex + playbackSpeed) % lapData.data.length);
    }, 50);

    return () => clearInterval(interval);
  }, [isPlaying, currentIndex, playbackSpeed, lapData, setCurrentIndex]);

  return (
    <>
      <PerspectiveCamera
        ref={cameraRef}
        makeDefault
        position={[
          carState.position[0] - Math.sin(carState.rotation) * 8,
          5,
          carState.position[2] - Math.cos(carState.rotation) * 8,
        ]}
        fov={60}
      />

      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight
        position={[50, 100, 50]}
        intensity={1}
        castShadow
        shadow-mapSize={[2048, 2048]}
      />
      <pointLight position={[0, 50, 0]} intensity={0.5} color="#ffffff" />

      {/* Stadium lights effect */}
      {[[-30, 20, -30], [30, 20, -30], [-30, 20, 30], [30, 20, 30]].map((pos, i) => (
        <pointLight key={i} position={pos as [number, number, number]} intensity={0.3} color="#fff5e6" />
      ))}

      {/* Sky */}
      <Sky sunPosition={[100, 20, 100]} />

      {/* Environment */}
      <Environment preset="night" />

      {/* Track */}
      {lapData?.data && <RaceTrack trackData={lapData.data} scale={scale} />}

      {/* Car */}
      <RacingCar
        position={carState.position}
        rotation={carState.rotation}
        speed={carState.speed}
      />

      {/* Controls - only active when not following car */}
      <OrbitControls
        target={carState.position}
        enablePan={true}
        enableZoom={true}
        maxDistance={100}
        minDistance={5}
      />
    </>
  );
}

export function Scene3D() {
  return (
    <div className="w-full h-full rounded-xl overflow-hidden border border-white/10">
      <Canvas shadows>
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
    </div>
  );
}
