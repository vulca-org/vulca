import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useTheme } from '../../contexts/useTheme';

// Subtle ambient colors for light/dark themes
const COLORS = {
  dark: {
    background: '#0F0D0B',
    shapes: [
      { color: '#C87F4A', opacity: 0.06 },  // Warm Bronze
      { color: '#334155', opacity: 0.05 },   // Ink Slate
      { color: '#B8923D', opacity: 0.04 },   // Amber Gold
    ],
  },
  light: {
    background: '#f9f9ff',
    shapes: [
      { color: '#414753', opacity: 0.04 },   // MD3 on-surface-variant
      { color: '#C87F4A', opacity: 0.035 },  // Warm Bronze
      { color: '#414753', opacity: 0.03 },    // MD3 on-surface-variant lighter
    ],
  },
};

// A single slowly drifting translucent shape
function DriftingShape({
  position,
  scale,
  speed,
  color,
  opacity,
  shapeType,
}: {
  position: [number, number, number];
  scale: number;
  speed: number;
  color: string;
  opacity: number;
  shapeType: 'sphere' | 'torus' | 'octahedron';
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const initialY = position[1];

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (meshRef.current) {
      // Gentle floating motion
      meshRef.current.position.y = initialY + Math.sin(t * speed * 0.3) * 0.4;
      meshRef.current.position.x = position[0] + Math.sin(t * speed * 0.2 + 1.5) * 0.2;
      // Very slow rotation
      meshRef.current.rotation.x += speed * 0.001;
      meshRef.current.rotation.y += speed * 0.0015;
    }
  });

  const geometry = useMemo(() => {
    switch (shapeType) {
      case 'sphere':
        return new THREE.SphereGeometry(scale, 16, 12);
      case 'torus':
        return new THREE.TorusGeometry(scale, scale * 0.3, 12, 24);
      case 'octahedron':
        return new THREE.OctahedronGeometry(scale);
    }
  }, [scale, shapeType]);

  const material = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity,
        wireframe: true,
        depthWrite: false,
      }),
    [color, opacity]
  );

  return <mesh ref={meshRef} position={position} geometry={geometry} material={material} />;
}

// Main scene with a few ambient shapes
function Scene({ isDark }: { isDark: boolean }) {
  const palette = isDark ? COLORS.dark : COLORS.light;

  const shapes = useMemo(() => {
    const shapeTypes: Array<'sphere' | 'torus' | 'octahedron'> = [
      'octahedron',
      'sphere',
      'torus',
      'octahedron',
      'sphere',
    ];

    return [
      { position: [-4, 1.5, -3] as [number, number, number], scale: 2.0, speed: 0.4, ...palette.shapes[0], shapeType: shapeTypes[0] },
      { position: [4.5, -1, -4] as [number, number, number], scale: 2.5, speed: 0.3, ...palette.shapes[1], shapeType: shapeTypes[1] },
      { position: [0, 2.5, -5] as [number, number, number], scale: 1.8, speed: 0.35, ...palette.shapes[2], shapeType: shapeTypes[2] },
      { position: [-3, -2, -4] as [number, number, number], scale: 1.5, speed: 0.25, ...palette.shapes[0], shapeType: shapeTypes[3] },
      { position: [3, 0, -6] as [number, number, number], scale: 2.2, speed: 0.2, ...palette.shapes[1], shapeType: shapeTypes[4] },
    ];
  }, [palette]);

  return (
    <>
      <color attach="background" args={[palette.background]} />
      {shapes.map((shape, i) => (
        <DriftingShape key={i} {...shape} />
      ))}
    </>
  );
}

// Performance detection
function useDevicePerformance(): 'high' | 'medium' | 'low' {
  const [level, setLevel] = useState<'high' | 'medium' | 'low'>('medium');

  useEffect(() => {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

    if (!gl) {
      setLevel('low');
      return;
    }

    const debugInfo = (gl as WebGLRenderingContext).getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      const renderer = (gl as WebGLRenderingContext).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
      if (renderer.includes('Intel') || renderer.includes('Mesa')) {
        setLevel('medium');
      } else {
        setLevel('high');
      }
    }
  }, []);

  return level;
}

// CSS fallback gradient for when WebGL is unavailable
function CSSFallback({ isDark }: { isDark: boolean }) {
  return (
    <div
      className="fixed inset-0 -z-10 transition-colors duration-500"
      style={{
        background: isDark
          ? `
            radial-gradient(ellipse at 25% 30%, rgba(200, 127, 74, 0.08) 0%, transparent 55%),
            radial-gradient(ellipse at 75% 65%, rgba(51, 65, 85, 0.06) 0%, transparent 55%),
            #0F0D0B
          `
          : `
            radial-gradient(ellipse at 25% 30%, rgba(200, 127, 74, 0.05) 0%, transparent 55%),
            radial-gradient(ellipse at 75% 65%, rgba(65, 71, 83, 0.04) 0%, transparent 55%),
            #f9f9ff
          `,
      }}
    />
  );
}

// Exported main component
export default function Vulca3DBackground() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const performance = useDevicePerformance();

  // Low-performance devices or no WebGL: CSS fallback
  if (performance === 'low') {
    return <CSSFallback isDark={isDark} />;
  }

  return (
    <div className="fixed inset-0 -z-10">
      {/* CSS fallback visible while Canvas loads or if WebGL fails */}
      <CSSFallback isDark={isDark} />
      <div className="absolute inset-0">
        <Canvas
          camera={{ position: [0, 0, 10], fov: 50, near: 0.1, far: 100 }}
          dpr={[1, 1.5]}
          gl={{
            antialias: false,
            alpha: false,
            powerPreference: 'low-power',
          }}
        >
          <Scene isDark={isDark} />
        </Canvas>
      </div>
    </div>
  );
}

// Simplified version for low-performance devices or first-screen loading
export function Vulca3DBackgroundSimple() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  return <CSSFallback isDark={isDark} />;
}
