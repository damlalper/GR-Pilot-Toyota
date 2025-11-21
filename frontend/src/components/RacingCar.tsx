import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface RacingCarProps {
  position: [number, number, number];
  rotation: number;
  speed: number;
  color?: string;
}

export function RacingCar({ position, rotation, speed, color = '#EB0A1E' }: RacingCarProps) {
  const carRef = useRef<THREE.Group>(null);
  const wheelsRef = useRef<THREE.Mesh[]>([]);

  useFrame(() => {
    // Rotate wheels based on speed
    wheelsRef.current.forEach((wheel) => {
      if (wheel) {
        wheel.rotation.x += speed * 0.01;
      }
    });
  });

  return (
    <group ref={carRef} position={position} rotation={[0, rotation, 0]}>
      {/* Car Body - Main chassis */}
      <mesh position={[0, 0.4, 0]}>
        <boxGeometry args={[2.2, 0.5, 4.5]} />
        <meshStandardMaterial color={color} metalness={0.8} roughness={0.2} />
      </mesh>

      {/* Car Body - Top/Cabin */}
      <mesh position={[0, 0.8, -0.3]}>
        <boxGeometry args={[1.8, 0.4, 2]} />
        <meshStandardMaterial color="#1a1a1a" metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Windshield */}
      <mesh position={[0, 0.85, 0.6]} rotation={[-0.3, 0, 0]}>
        <boxGeometry args={[1.6, 0.02, 0.8]} />
        <meshStandardMaterial color="#87CEEB" metalness={0.1} roughness={0.1} transparent opacity={0.7} />
      </mesh>

      {/* Rear Windshield */}
      <mesh position={[0, 0.85, -1.2]} rotation={[0.3, 0, 0]}>
        <boxGeometry args={[1.6, 0.02, 0.6]} />
        <meshStandardMaterial color="#87CEEB" metalness={0.1} roughness={0.1} transparent opacity={0.7} />
      </mesh>

      {/* Front Splitter */}
      <mesh position={[0, 0.15, 2.4]}>
        <boxGeometry args={[2.4, 0.1, 0.4]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>

      {/* Rear Wing - Supports */}
      <mesh position={[-0.6, 1, -2.1]}>
        <boxGeometry args={[0.1, 0.6, 0.1]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[0.6, 1, -2.1]}>
        <boxGeometry args={[0.1, 0.6, 0.1]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>

      {/* Rear Wing - Main */}
      <mesh position={[0, 1.3, -2.1]}>
        <boxGeometry args={[2, 0.05, 0.4]} />
        <meshStandardMaterial color={color} metalness={0.7} roughness={0.3} />
      </mesh>

      {/* Headlights */}
      <mesh position={[-0.6, 0.4, 2.3]}>
        <boxGeometry args={[0.4, 0.15, 0.1]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffff00" emissiveIntensity={0.5} />
      </mesh>
      <mesh position={[0.6, 0.4, 2.3]}>
        <boxGeometry args={[0.4, 0.15, 0.1]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffff00" emissiveIntensity={0.5} />
      </mesh>

      {/* Taillights */}
      <mesh position={[-0.7, 0.4, -2.25]}>
        <boxGeometry args={[0.3, 0.15, 0.05]} />
        <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={0.8} />
      </mesh>
      <mesh position={[0.7, 0.4, -2.25]}>
        <boxGeometry args={[0.3, 0.15, 0.05]} />
        <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={0.8} />
      </mesh>

      {/* Toyota Logo area */}
      <mesh position={[0, 0.65, 2.26]}>
        <boxGeometry args={[0.5, 0.2, 0.01]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>

      {/* Number plate background */}
      <mesh position={[0.8, 0.5, 0]}>
        <boxGeometry args={[0.01, 0.4, 0.6]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
      <mesh position={[-0.8, 0.5, 0]}>
        <boxGeometry args={[0.01, 0.4, 0.6]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>

      {/* Wheels */}
      {[
        [-0.95, 0.2, 1.4],
        [0.95, 0.2, 1.4],
        [-0.95, 0.2, -1.4],
        [0.95, 0.2, -1.4],
      ].map((pos, i) => (
        <group key={i} position={pos as [number, number, number]}>
          {/* Tire */}
          <mesh
            ref={(el) => { if (el) wheelsRef.current[i] = el; }}
            rotation={[0, 0, Math.PI / 2]}
          >
            <cylinderGeometry args={[0.35, 0.35, 0.3, 24]} />
            <meshStandardMaterial color="#1a1a1a" roughness={0.9} />
          </mesh>
          {/* Rim */}
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.2, 0.2, 0.32, 8]} />
            <meshStandardMaterial color="#888888" metalness={0.9} roughness={0.1} />
          </mesh>
        </group>
      ))}

      {/* Exhaust pipes */}
      <mesh position={[-0.4, 0.25, -2.3]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.2, 12]} />
        <meshStandardMaterial color="#444444" metalness={0.9} />
      </mesh>
      <mesh position={[0.4, 0.25, -2.3]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.2, 12]} />
        <meshStandardMaterial color="#444444" metalness={0.9} />
      </mesh>

      {/* Side mirrors */}
      <mesh position={[-1.1, 0.7, 0.8]}>
        <boxGeometry args={[0.15, 0.1, 0.2]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[1.1, 0.7, 0.8]}>
        <boxGeometry args={[0.15, 0.1, 0.2]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
}
