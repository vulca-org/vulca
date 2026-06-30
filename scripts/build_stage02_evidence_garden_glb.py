from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import struct
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden"
    / "assets"
    / "evidence-garden-blockout.glb"
)
DEFAULT_MANIFEST = DEFAULT_OUTPUT.with_name("asset-manifest.json")


Vec3 = tuple[float, float, float]


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _mul(a: Vec3, scalar: float) -> Vec3:
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _length(a: Vec3) -> float:
    return math.sqrt(_dot(a, a))


def _norm(a: Vec3) -> Vec3:
    length = _length(a)
    if length < 1e-8:
        return (0.0, 1.0, 0.0)
    return (a[0] / length, a[1] / length, a[2] / length)


def _align4(data: bytearray) -> None:
    while len(data) % 4:
        data.append(0)


class MeshBuilder:
    def __init__(self, name: str, material: int) -> None:
        self.name = name
        self.material = material
        self.positions: list[Vec3] = []
        self.normals: list[Vec3] = []
        self.indices: list[int] = []

    def add_vertex(self, position: Vec3, normal: Vec3) -> int:
        self.positions.append(position)
        self.normals.append(_norm(normal))
        return len(self.positions) - 1

    def add_triangle(self, a: int, b: int, c: int) -> None:
        self.indices.extend([a, b, c])

    def extend(self, positions: Iterable[Vec3], normals: Iterable[Vec3], indices: Iterable[int]) -> None:
        base = len(self.positions)
        self.positions.extend(positions)
        self.normals.extend(_norm(normal) for normal in normals)
        self.indices.extend(base + index for index in indices)


def add_ellipsoid(mesh: MeshBuilder, center: Vec3, radius: Vec3, rows: int = 14, cols: int = 28) -> None:
    positions: list[Vec3] = []
    normals: list[Vec3] = []
    indices: list[int] = []
    for row in range(rows + 1):
        theta = math.pi * row / rows
        for col in range(cols):
            phi = math.tau * col / cols
            sx = math.sin(theta) * math.cos(phi)
            sy = math.cos(theta)
            sz = math.sin(theta) * math.sin(phi)
            positions.append(
                (
                    center[0] + radius[0] * sx,
                    center[1] + radius[1] * sy,
                    center[2] + radius[2] * sz,
                )
            )
            normals.append(_norm((sx / max(radius[0], 0.001), sy / max(radius[1], 0.001), sz / max(radius[2], 0.001))))

    for row in range(rows):
        for col in range(cols):
            a = row * cols + col
            b = row * cols + (col + 1) % cols
            c = (row + 1) * cols + col
            d = (row + 1) * cols + (col + 1) % cols
            indices.extend([a, c, b, b, c, d])
    mesh.extend(positions, normals, indices)


def add_cylinder_between(mesh: MeshBuilder, start: Vec3, end: Vec3, radius: float, segments: int = 10) -> None:
    axis = _sub(end, start)
    direction = _norm(axis)
    helper = (0.0, 1.0, 0.0)
    if abs(_dot(direction, helper)) > 0.92:
        helper = (1.0, 0.0, 0.0)
    u = _norm(_cross(direction, helper))
    v = _norm(_cross(direction, u))
    ring_start: list[int] = []
    ring_end: list[int] = []
    for i in range(segments):
        angle = math.tau * i / segments
        radial = _add(_mul(u, math.cos(angle)), _mul(v, math.sin(angle)))
        ring_start.append(mesh.add_vertex(_add(start, _mul(radial, radius)), radial))
        ring_end.append(mesh.add_vertex(_add(end, _mul(radial, radius)), radial))
    for i in range(segments):
        a = ring_start[i]
        b = ring_start[(i + 1) % segments]
        c = ring_end[i]
        d = ring_end[(i + 1) % segments]
        mesh.add_triangle(a, c, b)
        mesh.add_triangle(b, c, d)


def add_polyline_cylinders(mesh: MeshBuilder, points: list[Vec3], radius: float, segments: int = 8) -> None:
    for start, end in zip(points, points[1:]):
        add_cylinder_between(mesh, start, end, radius, segments)


def create_garden_meshes() -> tuple[list[MeshBuilder], list[dict[str, object]]]:
    materials = [
        {
            "name": "dark_graphite_mineral",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.08, 0.11, 0.09, 1.0],
                "metallicFactor": 0.12,
                "roughnessFactor": 0.78,
            },
        },
        {
            "name": "translucent_glass_roots",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.72, 0.95, 0.9, 0.42],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.18,
            },
            "alphaMode": "BLEND",
            "doubleSided": True,
        },
        {
            "name": "cyan_route_veins",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.16, 0.82, 0.78, 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.25,
            },
            "emissiveFactor": [0.08, 0.45, 0.42],
        },
        {
            "name": "warm_data_blossoms",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.88, 0.52, 0.25, 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.36,
            },
            "emissiveFactor": [0.55, 0.24, 0.08],
        },
        {
            "name": "moss_specimen_surface",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.36, 0.46, 0.29, 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.82,
            },
        },
    ]

    island = MeshBuilder("evidence_garden_mineral_island", 0)
    add_ellipsoid(island, (0.0, 0.0, 0.0), (1.95, 0.32, 1.08), 16, 34)
    add_ellipsoid(island, (0.18, 0.18, -0.06), (1.42, 0.18, 0.76), 10, 28)

    moss = MeshBuilder("evidence_garden_moss_specimen_surface", 4)
    add_ellipsoid(moss, (-0.18, 0.31, -0.04), (1.18, 0.035, 0.58), 6, 28)

    roots = MeshBuilder("evidence_garden_translucent_roots", 1)
    root_paths = [
        [(-0.9, -0.02, 0.18), (-1.05, -0.45, 0.36), (-0.72, -0.92, 0.82)],
        [(-0.5, -0.03, -0.12), (-0.68, -0.52, -0.38), (-0.28, -1.05, -0.72)],
        [(-0.05, 0.0, 0.1), (0.08, -0.58, 0.02), (0.24, -1.08, 0.38)],
        [(0.46, -0.01, -0.04), (0.82, -0.45, -0.18), (1.08, -0.94, -0.64)],
        [(0.86, 0.0, 0.18), (1.08, -0.48, 0.22), (0.86, -0.96, 0.72)],
        [(0.18, 0.0, -0.34), (0.0, -0.48, -0.58), (-0.46, -0.96, -0.96)],
    ]
    for path in root_paths:
        add_polyline_cylinders(roots, path, 0.025, 9)

    routes = MeshBuilder("evidence_garden_luminous_route_veins", 2)
    route_paths = [
        [(-1.28, 0.36, 0.02), (-0.72, 0.42, 0.14), (-0.1, 0.39, -0.04), (0.62, 0.42, 0.18), (1.18, 0.36, 0.08)],
        [(-0.84, 0.38, -0.42), (-0.22, 0.43, -0.22), (0.35, 0.4, -0.34), (0.92, 0.36, -0.2)],
        [(-0.56, 0.37, 0.48), (-0.08, 0.44, 0.24), (0.48, 0.4, 0.46)],
        [(-0.18, 0.38, -0.58), (-0.08, 0.44, -0.12), (0.04, 0.4, 0.5)],
    ]
    for path in route_paths:
        add_polyline_cylinders(routes, path, 0.018, 8)

    blossoms = MeshBuilder("evidence_garden_warm_data_blossoms", 3)
    blossom_centers = [(-0.78, 0.58, 0.18), (-0.16, 0.64, -0.12), (0.54, 0.58, 0.28), (0.95, 0.52, -0.18)]
    for index, center in enumerate(blossom_centers):
        add_cylinder_between(blossoms, (center[0], 0.39, center[2]), (center[0], center[1] - 0.08, center[2]), 0.012, 8)
        add_ellipsoid(blossoms, center, (0.09, 0.13 + index * 0.01, 0.09), 8, 14)
        add_ellipsoid(blossoms, (center[0], center[1] + 0.045, center[2]), (0.045, 0.045, 0.045), 6, 10)

    particles = MeshBuilder("evidence_garden_archive_seed_particles", 3)
    particle_centers = [
        (-0.98, 0.86, -0.2),
        (-0.52, 1.04, 0.38),
        (0.02, 0.94, -0.5),
        (0.38, 1.16, 0.18),
        (0.88, 0.98, 0.48),
        (1.12, 0.78, -0.12),
    ]
    for center in particle_centers:
        add_ellipsoid(particles, center, (0.035, 0.035, 0.035), 5, 8)

    return [island, moss, roots, routes, blossoms, particles], materials


def _pack_floats(values: Iterable[float]) -> bytes:
    value_list = list(values)
    return struct.pack("<" + "f" * len(value_list), *value_list)


def _pack_uint16(values: Iterable[int]) -> bytes:
    value_list = list(values)
    return struct.pack("<" + "H" * len(value_list), *value_list)


def _append_view(binary: bytearray, data: bytes, target: int | None = None) -> dict[str, object]:
    _align4(binary)
    offset = len(binary)
    binary.extend(data)
    _align4(binary)
    view: dict[str, object] = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
    if target is not None:
        view["target"] = target
    return view


def build_glb(output: Path, manifest_path: Path) -> None:
    meshes, materials = create_garden_meshes()
    binary = bytearray()
    gltf: dict[str, object] = {
        "asset": {
            "version": "2.0",
            "generator": "vulca stage02 evidence garden procedural blockout",
            "copyright": "Generated procedural geometry for internal review.",
        },
        "scene": 0,
        "scenes": [{"name": "evidence_garden_blockout_scene", "nodes": list(range(len(meshes)))}],
        "nodes": [],
        "meshes": [],
        "materials": materials,
        "buffers": [{"byteLength": 0}],
        "bufferViews": [],
        "accessors": [],
    }

    buffer_views: list[dict[str, object]] = gltf["bufferViews"]  # type: ignore[assignment]
    accessors: list[dict[str, object]] = gltf["accessors"]  # type: ignore[assignment]
    gltf_meshes: list[dict[str, object]] = gltf["meshes"]  # type: ignore[assignment]
    nodes: list[dict[str, object]] = gltf["nodes"]  # type: ignore[assignment]

    for mesh_index, mesh in enumerate(meshes):
        positions_flat = [component for position in mesh.positions for component in position]
        normals_flat = [component for normal in mesh.normals for component in normal]
        position_view_index = len(buffer_views)
        buffer_views.append(_append_view(binary, _pack_floats(positions_flat), 34962))
        normal_view_index = len(buffer_views)
        buffer_views.append(_append_view(binary, _pack_floats(normals_flat), 34962))
        index_view_index = len(buffer_views)
        buffer_views.append(_append_view(binary, _pack_uint16(mesh.indices), 34963))

        mins = [min(position[i] for position in mesh.positions) for i in range(3)]
        maxs = [max(position[i] for position in mesh.positions) for i in range(3)]
        position_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": position_view_index,
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(mesh.positions),
                "type": "VEC3",
                "min": mins,
                "max": maxs,
            }
        )
        normal_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": normal_view_index,
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(mesh.normals),
                "type": "VEC3",
            }
        )
        index_accessor = len(accessors)
        accessors.append(
            {
                "bufferView": index_view_index,
                "byteOffset": 0,
                "componentType": 5123,
                "count": len(mesh.indices),
                "type": "SCALAR",
            }
        )

        gltf_meshes.append(
            {
                "name": mesh.name,
                "primitives": [
                    {
                        "attributes": {"POSITION": position_accessor, "NORMAL": normal_accessor},
                        "indices": index_accessor,
                        "material": mesh.material,
                    }
                ],
            }
        )
        nodes.append({"name": mesh.name, "mesh": mesh_index})

    gltf["buffers"] = [{"byteLength": len(binary)}]
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4:
        json_bytes += b" "

    glb = bytearray()
    total_length = 12 + 8 + len(json_bytes) + 8 + len(binary)
    glb.extend(struct.pack("<III", 0x46546C67, 2, total_length))
    glb.extend(struct.pack("<I4s", len(json_bytes), b"JSON"))
    glb.extend(json_bytes)
    glb.extend(struct.pack("<I4s", len(binary), b"BIN\x00"))
    glb.extend(binary)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(glb)
    try:
        manifest_asset_path = str(output.relative_to(REPO_ROOT))
    except ValueError:
        manifest_asset_path = str(output)
    manifest = {
        "asset_id": "evidence-garden-blockout",
        "path": manifest_asset_path,
        "format": "glb",
        "source": "procedural_blockout",
        "generated_by": "scripts/build_stage02_evidence_garden_glb.py",
        "intent": "Baseline local GLB for Evidence Garden first-frame and model-viewer smoke review.",
        "model_parts": [mesh.name for mesh in meshes],
        "materials": [material["name"] for material in materials],
        "rights_status": "generated_local_procedural",
        "do_not_treat_as_final_asset": True,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Stage 02 Evidence Garden procedural GLB blockout.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    build_glb(args.output, args.manifest)
    print(f"wrote {args.output}")
    print(f"wrote {args.manifest}")


if __name__ == "__main__":
    main()
