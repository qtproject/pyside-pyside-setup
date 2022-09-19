// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include <QtGui/QOpenGLFunctions>

// Return the number of return values of the glGetBoolean/Double/Integerv functions
// cf https://registry.khronos.org/OpenGL-Refpages/gl4/html/glGet.xhtml
int glGetVReturnSize(GLenum pname)
{
    switch (pname) {
    case GL_ALIASED_LINE_WIDTH_RANGE:
    case GL_DEPTH_RANGE:
    case GL_MAX_VIEWPORT_DIMS:
#if !QT_CONFIG(opengles2)
    case GL_POINT_SIZE_RANGE:
    case GL_SMOOTH_LINE_WIDTH_RANGE:
    case GL_VIEWPORT_BOUNDS_RANGE:
#endif
        return 2;
    case GL_BLEND_COLOR:
    case GL_COLOR_CLEAR_VALUE:
    case GL_COLOR_WRITEMASK:
    case GL_SCISSOR_BOX:
    case GL_VIEWPORT:
        return 4;
    case GL_COMPRESSED_TEXTURE_FORMATS:
        return GL_NUM_COMPRESSED_TEXTURE_FORMATS;
    default:
        break;
    }
    return 1;
}

// Return the number of return values of the indexed
// glGetBoolean/Double/Integeri_v functions
// cf https://registry.khronos.org/OpenGL-Refpages/gl4/html/glGet.xhtml
int glGetI_VReturnSize(GLenum pname)
{
    return pname == GL_VIEWPORT ? 4 : 1;
}
