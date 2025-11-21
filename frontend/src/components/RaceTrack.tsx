import { useMemo } from 'react';
import * as THREE from 'three';
import { TelemetryPoint } from '../types';

interface RaceTrackProps {
  trackData: TelemetryPoint[];
  scale?: number;
}

export function RaceTrack({ trackData, scale = 0.01 }: RaceTrackProps) {
  const { trackPath, trackWidth } = useMemo(() => {
    if (!trackData || trackData.length < 2) return { trackPath: [], trackWidth: 12 };

    // Normalize and center track
    const minX = Math.min(...trackData.map((p) => p.WorldPositionX));
    const maxX = Math.max(...trackData.map((p) => p.WorldPositionX));
    const minY = Math.min(...trackData.map((p) => p.WorldPositionY));
    const maxY = Math.max(...trackData.map((p) => p.WorldPositionY));

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    const path = trackData.map((p) => ({
      x: (p.WorldPositionX - centerX) * scale,
      z: (p.WorldPositionY - centerY) * scale,
      speed: p.speed,
    }));

    return { trackPath: path, trackWidth: 12 };
  }, [trackData, scale]);

  const trackGeometry = useMemo(() => {
    if (trackPath.length < 2) return null;

    const points = trackPath.map((p) => new THREE.Vector3(p.x, 0, p.z));
    const curve = new THREE.CatmullRomCurve3(points, true);
    const tubeGeometry = new THREE.TubeGeometry(curve, trackPath.length * 2, 0.5, 8, true);

    return tubeGeometry;
  }, [trackPath]);

  const trackSurfaceGeometry = useMemo(() => {
    if (trackPath.length < 2) return null;

    const shape = new THREE.Shape();
    trackPath.forEach((p, i) => {
      if (i === 0) shape.moveTo(p.x, p.z);
      else shape.lineTo(p.x, p.z);
    });

    const geometry = new THREE.ShapeGeometry(shape);
    geometry.rotateX(-Math.PI / 2);

    return geometry;
  }, [trackPath]);

  // Create racing line with speed-based colors
  const racingLinePoints = useMemo(() => {
    return trackPath.map((p) => new THREE.Vector3(p.x, 0.05, p.z));
  }, [trackPath]);

  const racingLineColors = useMemo(() => {
    const maxSpeed = Math.max(...trackPath.map((p) => p.speed || 0));
    return trackPath.map((p) => {
      const ratio = (p.speed || 0) / maxSpeed;
      // Red for fast, blue for slow
      return new THREE.Color().setHSL(0.6 - ratio * 0.6, 1, 0.5);
    });
  }, [trackPath]);

  if (!trackGeometry) return null;

  return (
    <group>
      {/* Track surface - asphalt */}
      <mesh rotation={[0, 0, 0]} position={[0, -0.1, 0]}>
        <planeGeometry args={[200, 200]} />
        <meshStandardMaterial color="#1a1a1a" roughness={0.9} />
      </mesh>

      {/* Main track path */}
      <mesh geometry={trackGeometry}>
        <meshStandardMaterial
          color="#2a2a2a"
          roughness={0.8}
          metalness={0.1}
        />
      </mesh>

      {/* Track boundaries - white lines */}
      {trackPath.length > 0 && (
        <>
          <line>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={racingLinePoints.length}
                array={new Float32Array(racingLinePoints.flatMap((p) => [p.x - 0.6, 0.02, p.z]))}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#ffffff" linewidth={2} />
          </line>
          <line>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={racingLinePoints.length}
                array={new Float32Array(racingLinePoints.flatMap((p) => [p.x + 0.6, 0.02, p.z]))}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#ffffff" linewidth={2} />
          </line>
        </>
      )}

      {/* Racing line with speed gradient */}
      {racingLinePoints.length > 1 && (
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={racingLinePoints.length}
              array={new Float32Array(racingLinePoints.flatMap((p) => [p.x, p.y, p.z]))}
              itemSize={3}
            />
            <bufferAttribute
              attach="attributes-color"
              count={racingLineColors.length}
              array={new Float32Array(racingLineColors.flatMap((c) => [c.r, c.g, c.b]))}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial vertexColors linewidth={3} />
        </line>
      )}

      {/* Start/Finish line */}
      {trackPath.length > 0 && (
        <mesh position={[trackPath[0].x, 0.01, trackPath[0].z]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[1.5, 0.3]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      )}

      {/* Grass areas */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.15, 0]}>
        <planeGeometry args={[300, 300]} />
        <meshStandardMaterial color="#1a3d1a" roughness={1} />
      </mesh>

      {/* Ambient environment */}
      <fog attach="fog" args={['#0a0a15', 50, 200]} />
    </group>
  );
}
