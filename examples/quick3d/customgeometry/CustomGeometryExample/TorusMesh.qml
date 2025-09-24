// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick3D.Helpers

ProceduralMesh {
    property int rings: 50
    property int segments: 50
    property real radius: 100.0
    property real tubeRadius: 10.0
    property var meshArrays: generateTorus(rings, segments, radius, tubeRadius)
    positions: meshArrays.verts
    normals: meshArrays.normals
    uv0s: meshArrays.uvs
    indexes: meshArrays.indices

    function generateTorus(rings: int, segments: int, radius: real, tubeRadius: real) : var {
        let verts = []
        let normals = []
        let uvs = []
        let indices = []

        for (let i = 0; i <= rings; ++i) {
            for (let j = 0; j <= segments; ++j) {
                const u = i / rings * Math.PI * 2;
                const v = j / segments * Math.PI * 2;

                const centerX = radius * Math.cos(u);
                const centerZ = radius * Math.sin(u);

                const posX = centerX + tubeRadius * Math.cos(v) * Math.cos(u);
                const posY = tubeRadius * Math.sin(v);
                const posZ = centerZ + tubeRadius * Math.cos(v) * Math.sin(u);

                verts.push(Qt.vector3d(posX, posY, posZ));

                const normal = Qt.vector3d(posX - centerX, posY, posZ - centerZ).normalized();
                normals.push(normal);

                uvs.push(Qt.vector2d(i / rings, j / segments));
            }
        }

        for (let i = 0; i < rings; ++i) {
            for (let j = 0; j < segments; ++j) {
                const a = (segments + 1) * i + j;
                const b = (segments + 1) * (i + 1) + j;
                const c = (segments + 1) * (i + 1) + j + 1;
                const d = (segments + 1) * i + j + 1;

                // Generate two triangles for each quad in the mesh
                // Adjust order to be counter-clockwise
                indices.push(a, d, b);
                indices.push(b, d, c);
            }
        }
        return { verts: verts, normals: normals, uvs: uvs, indices: indices }
    }
}
