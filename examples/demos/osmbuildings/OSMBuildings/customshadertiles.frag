// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

void MAIN() {
    vec2 tc = UV0;
    BASE_COLOR = vec4( texture(tileTexture, vec2(tc.x, 1.0 - tc.y )).xyz, 1.0 );
    ROUGHNESS = 0.3;
    METALNESS = 0.0;
    FRESNEL_POWER = 1.0;
}
