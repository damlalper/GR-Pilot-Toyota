import { useMemo } from 'react';
import * as THREE from 'three';
import { TelemetryPoint } from '../types';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';

interface EnhancedRaceTrackProps {
  trackData: TelemetryPoint[];
  currentPosition?: number;
  scale?: number;
}

// COTA Circuit of the Americas - 19 Turn Layout
const COTA_TURNS = [
  { turn: 1, angle: 133, elevation: 40, name: "Turn 1 - Uphill Hairpin", sector: 1 },
  { turn: 2, angle: -45, elevation: 35, name: "Turn 2", sector: 1 },
  { turn: 3, angle: -90, elevation: 30, name: "Turn 3 - Esse", sector: 1 },
  { turn: 4, angle: 90, elevation: 25, name: "Turn 4 - Esse", sector: 1 },
  { turn: 5, angle: -45, elevation: 20, name: "Turn 5", sector: 1 },
  { turn: 6, angle: 90, elevation: 15, name: "Turn 6 - Hairpin", sector: 2 },
  { turn: 7, angle: -30, elevation: 10, name: "Turn 7", sector: 2 },
  { turn: 8, angle: -45, elevation: 5, name: "Turn 8", sector: 2 },
  { turn: 9, angle: -60, elevation: 0, name: "Turn 9", sector: 2 },
  { turn: 10, angle: 45, elevation: -5, name: "Turn 10", sector: 2 },
  { turn: 11, angle: 90, elevation: -10, name: "Turn 11 - Hairpin", sector: 2 },
  { turn: 12, angle: -90, elevation: 0, name: "Turn 12 - Stadium", sector: 3 },
  { turn: 13, angle: -45, elevation: 5, name: "Turn 13", sector: 3 },
  { turn: 14, angle: -30, elevation: 10, name: "Turn 14", sector: 3 },
  { turn: 15, angle: -90, elevation: 15, name: "Turn 15 - Hairpin", sector: 3 },
  { turn: 16, angle: 45, elevation: 10, name: "Turn 16", sector: 3 },
  { turn: 17, angle: -45, elevation: 5, name: "Turn 17", sector: 3 },
  { turn: 18, angle: -60, elevation: 0, name: "Turn 18", sector: 3 },
  { turn: 19, angle: -90, elevation: 0, name: "Turn 19 - Back Straight", sector: 3 },
];

export function EnhancedRaceTrack({ trackData, currentPosition = 0, scale = 0.01 }: EnhancedRaceTrackProps) {

  // Create realistic COTA track with elevation
  const trackGeometry = useMemo(() => {
    if (!trackData || trackData.length < 10) return null;

    // Sample points for smoother curve
    const samplePoints: THREE.Vector3[] = [];
    const colors: number[] = [];

    trackData.forEach((point, i) => {
      if (i % 3 === 0) { // Sample every 3rd point for performance
        const x = (point.WorldPositionX || 0) * scale;
        const z = (point.WorldPositionY || 0) * scale;

        // Add elevation based on track position (simulate COTA elevation changes)
        const progress = i / trackData.length;
        let y = 0;

        // Turn 1 uphill (0-10%)
        if (progress < 0.1) {
          y = Math.sin(progress * Math.PI * 5) * 2;
        }
        // Downhill section (10-30%)
        else if (progress < 0.3) {
          y = 2 - ((progress - 0.1) / 0.2) * 3;
        }
        // Stadium section (70-85%)
        else if (progress > 0.7 && progress < 0.85) {
          y = -1 + Math.sin((progress - 0.7) * Math.PI * 4) * 0.5;
        }

        samplePoints.push(new THREE.Vector3(x, y, z));

        // Color based on speed (green = fast, red = slow)
        const speed = point.speed || 0;
        const speedRatio = Math.min(speed / 200, 1); // Normalize to 0-1
        colors.push(
          1 - speedRatio,  // R: high when slow
          speedRatio,      // G: high when fast
          0.2              // B: constant blue tint
        );
      }
    });

    // Create smooth curve
    const curve = new THREE.CatmullRomCurve3(samplePoints, true, 'catmullrom', 0.5);

    // Create tube geometry for track surface
    const tubeGeometry = new THREE.TubeGeometry(
      curve,
      samplePoints.length * 2,
      0.8,  // Track width
      16,   // Radial segments (smoothness)
      true  // Closed loop
    );

    // Apply speed colors to geometry
    const colorAttribute = new THREE.Float32BufferAttribute(
      colors.flatMap(c => [c, c, c]), // Repeat for each vertex
      3
    );
    tubeGeometry.setAttribute('color', colorAttribute);

    return { geometry: tubeGeometry, curve };
  }, [trackData, scale]);

  // Asphalt texture with kerbs
  const trackMaterial = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: '#2a2a2a',
      roughness: 0.7,
      metalness: 0.3,
      vertexColors: true,
      emissive: '#111111',
      emissiveIntensity: 0.2,
    });
  }, []);

  // Racing line (ideal path)
  const racingLine = useMemo(() => {
    if (!trackGeometry?.curve) return null;

    const points = trackGeometry.curve.getPoints(200);
    const linePoints = points.map(p => new THREE.Vector3(p.x, p.y + 0.05, p.z));

    return linePoints;
  }, [trackGeometry]);

  // Sector markers
  const sectorMarkers = useMemo(() => {
    if (!trackData || trackData.length === 0) return [];

    const totalPoints = trackData.length;
    return [
      { position: 0, sector: 1, color: '#3b82f6' },      // Sector 1 - Blue
      { position: totalPoints * 0.33, sector: 2, color: '#10b981' }, // Sector 2 - Green
      { position: totalPoints * 0.66, sector: 3, color: '#f59e0b' }, // Sector 3 - Yellow
    ];
  }, [trackData]);

  // GPS Trail Effect - Show car's path with fade
  const gpsTrail = useMemo(() => {
    if (!trackData || currentPosition === undefined) return null;

    const trailLength = 50; // Number of points in trail
    const startIdx = Math.max(0, currentPosition - trailLength);
    const endIdx = currentPosition;

    const points: THREE.Vector3[] = [];
    const colors: number[] = [];

    for (let i = startIdx; i <= endIdx; i++) {
      const point = trackData[i];
      if (point) {
        const x = (point.WorldPositionX || 0) * scale;
        const z = (point.WorldPositionY || 0) * scale;
        const y = 0.2; // Slightly above track

        points.push(new THREE.Vector3(x, y, z));

        // Fade from red (recent) to transparent (old)
        const fadeRatio = (i - startIdx) / trailLength;
        colors.push(0.92, 0.04, 0.12, fadeRatio * 0.8); // RGBA
      }
    }

    return points;
  }, [trackData, currentPosition, scale]);

  if (!trackGeometry) return null;

  return (
    <group>
      {/* Main Track Surface with Speed Heatmap */}
      <mesh geometry={trackGeometry.geometry} material={trackMaterial} castShadow receiveShadow>
        <meshStandardMaterial
          color="#2a2a2a"
          roughness={0.8}
          metalness={0.2}
          vertexColors
        />
      </mesh>

      {/* GPS Trail Effect */}
      {gpsTrail && gpsTrail.length > 1 && (
        <Line
          points={gpsTrail}
          color="#eb0a1e"
          lineWidth={4}
          transparent
          opacity={0.8}
        />
      )}

      {/* Racing Line (red line) */}
      {racingLine && (
        <Line
          points={racingLine}
          color="#eb0a1e"
          lineWidth={2}
          dashed={false}
          transparent
          opacity={0.6}
        />
      )}

      {/* Sector Markers */}
      {sectorMarkers.map((marker, i) => {
        const point = trackData[Math.floor(marker.position)];
        if (!point) return null;

        return (
          <group key={i} position={[
            (point.WorldPositionX || 0) * scale,
            2,
            (point.WorldPositionY || 0) * scale
          ]}>
            {/* Sector Beam */}
            <mesh>
              <cylinderGeometry args={[0.5, 0.5, 4, 16]} />
              <meshStandardMaterial
                color={marker.color}
                emissive={marker.color}
                emissiveIntensity={0.8}
                transparent
                opacity={0.6}
              />
            </mesh>

            {/* Sector Number */}
            <mesh position={[0, 3, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <circleGeometry args={[0.8, 32]} />
              <meshBasicMaterial color={marker.color} />
            </mesh>
          </group>
        );
      })}

      {/* Ambient Ground Plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]} receiveShadow>
        <planeGeometry args={[300, 300]} />
        <meshStandardMaterial color="#1a1a1a" roughness={0.9} />
      </mesh>

      {/* Grid Lines */}
      <gridHelper args={[200, 20, '#333333', '#222222']} position={[0, -0.4, 0]} />

      {/* Start/Finish Line */}
      <mesh position={[0, 0.1, 0]} rotation={[0, 0, 0]}>
        <boxGeometry args={[2, 0.05, 1]} />
        <meshStandardMaterial
          color="#ffffff"
          emissive="#ffffff"
          emissiveIntensity={0.5}
        />
      </mesh>
    </group>
  );
}
