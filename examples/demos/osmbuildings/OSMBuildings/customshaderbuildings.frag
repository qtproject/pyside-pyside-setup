// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

VARYING vec4 color;

float rectangle(vec2 samplePosition, vec2 halfSize) {
    vec2 componentWiseEdgeDistance = abs(samplePosition) - halfSize;
    float outsideDistance = length(max(componentWiseEdgeDistance, 0.0));
    float insideDistance = min(max(componentWiseEdgeDistance.x, componentWiseEdgeDistance.y), 0.0);
    return outsideDistance + insideDistance;
}

void MAIN() {
    vec2 tc = UV0;
    vec2 uv = fract(tc * UV1.x); //UV1.x number of levels
    uv = uv * 2.0 - 1.0;
    uv.x = 0.0;
    uv.y = smoothstep(0.0, 0.2, rectangle( vec2(uv.x, uv.y + 0.5), vec2(0.2)) );
    BASE_COLOR = vec4(color.xyz * mix( clamp( ( vec3( 0.4, 0.4, 0.4 ) + tc.y)
                                             * ( vec3( 0.6, 0.6, 0.6 ) + uv.y)
                                             , 0.0, 1.0), vec3(1.0), UV1.y ), 1.0); // UV1.y as is roofTop
    ROUGHNESS = 0.3;
    METALNESS = 0.0;
    FRESNEL_POWER = 1.0;
}
