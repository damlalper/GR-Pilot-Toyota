import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, Sky } from '@react-three/drei';
import { Suspense, useMemo, useEffect, useRef } from 'react';
import { RacingCar } from './RacingCar';
import { RaceTrack } from './RaceTrack';
import { useStore } from '../store/useStore';
import * as THREE from 'three';

function SceneCompare() {
  const { lapData, comparisonLapData, currentIndex, isPlaying, playbackSpeed, setCurrentIndex } = useStore();
  const cameraRef = useRef<THREE.PerspectiveCamera>(null);

  const scale = 0.01;
  const trackOffset = 8; // Distance between two tracks (reduced for better view)

  // Calculate track center for normalization (for left track)
  const trackCenter = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) return { x: 0, y: 0 };
    const minX = Math.min(...lapData.data.map((p) => p.WorldPositionX));
    const maxX = Math.max(...lapData.data.map((p) => p.WorldPositionX));
    const minY = Math.min(...lapData.data.map((p) => p.WorldPositionY));
    const maxY = Math.max(...lapData.data.map((p) => p.WorldPositionY));
    return { x: (minX + maxX) / 2, y: (minY + maxY) / 2 };
  }, [lapData]);

  // LEFT TRACK - Current Lap (Blue Car)
  const leftCarState = useMemo(() => {
    if (!lapData?.data || lapData.data.length === 0) {
      return { position: [0, 0, 0] as [number, number, number], rotation: 0, speed: 0 };
    }

    const idx = Math.min(currentIndex, lapData.data.length - 1);
    const current = lapData.data[idx];
    const next = lapData.data[Math.min(idx + 1, lapData.data.length - 1)];

    const x = (current.WorldPositionX - trackCenter.x) * scale - trackOffset;
    const z = (current.WorldPositionY - trackCenter.y) * scale;

    const dx = (next.WorldPositionX - current.WorldPositionX) * scale;
    const dz = (next.WorldPositionY - current.WorldPositionY) * scale;
    const rotation = Math.atan2(dx, dz);

    return {
      position: [x, 0, z] as [number, number, number],
      rotation,
      speed: current.speed || 0,
    };
  }, [lapData, currentIndex, trackCenter, scale, trackOffset]);

  // RIGHT TRACK - Comparison Lap (Green Car)
  const rightCarState = useMemo(() => {
    if (!comparisonLapData?.data || comparisonLapData.data.length === 0) {
      return { position: [0, 0, 0] as [number, number, number], rotation: 0, speed: 0 };
    }

    const idx = Math.min(currentIndex, comparisonLapData.data.length - 1);
    const current = comparisonLapData.data[idx];
    const next = comparisonLapData.data[Math.min(idx + 1, comparisonLapData.data.length - 1)];

    const x = (current.WorldPositionX - trackCenter.x) * scale + trackOffset;
    const z = (current.WorldPositionY - trackCenter.y) * scale;

    const dx = (next.WorldPositionX - current.WorldPositionX) * scale;
    const dz = (next.WorldPositionY - current.WorldPositionY) * scale;
    const rotation = Math.atan2(dx, dz);

    return {
      position: [x, 0, z] as [number, number, number],
      rotation,
      speed: current.speed || 0,
    };
  }, [comparisonLapData, currentIndex, trackCenter, scale, trackOffset]);

  // Animation loop
  useEffect(() => {
    if (!isPlaying || !lapData?.data) return;

    const interval = setInterval(() => {
      setCurrentIndex((currentIndex + playbackSpeed) % lapData.data.length);
    }, 50);

    return () => clearInterval(interval);
  }, [isPlaying, currentIndex, playbackSpeed, lapData, setCurrentIndex]);

  // Camera position - centered between both tracks, higher and further for better overview
  const cameraPosition = useMemo(() => {
    return [0, 25, -25] as [number, number, number];
  }, []);

  return (
    <>
      <PerspectiveCamera
        ref={cameraRef}
        makeDefault
        position={cameraPosition}
        fov={90}
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

      {/* LEFT TRACK (Current Lap) */}
      {lapData?.data && (
        <group position={[-trackOffset, 0, 0]}>
          <RaceTrack trackData={lapData.data} scale={scale} />
        </group>
      )}

      {/* RIGHT TRACK (Comparison Lap) */}
      {comparisonLapData?.data && (
        <group position={[trackOffset, 0, 0]}>
          <RaceTrack trackData={comparisonLapData.data} scale={scale} />
        </group>
      )}

      {/* LEFT CAR - Blue (Current Lap) */}
      <RacingCar
        position={leftCarState.position}
        rotation={leftCarState.rotation}
        speed={leftCarState.speed}
        color="#3b82f6"
      />

      {/* RIGHT CAR - Green (Comparison Lap) */}
      {comparisonLapData?.data && (
        <RacingCar
          position={rightCarState.position}
          rotation={rightCarState.rotation}
          speed={rightCarState.speed}
          color="#22c55e"
        />
      )}

      {/* Controls */}
      <OrbitControls
        target={[0, 0, 0]}
        enablePan={true}
        enableZoom={true}
        maxDistance={100}
        minDistance={5}
      />
    </>
  );
}

export function Scene3DCompare() {
  return (
    <div className="w-full h-full rounded-xl overflow-hidden border border-white/10">
      <Canvas shadows>
        <Suspense fallback={null}>
          <SceneCompare />
        </Suspense>
      </Canvas>
    </div>
  );
}
