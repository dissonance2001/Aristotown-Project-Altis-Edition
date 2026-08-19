/*
  A fragment shader for testing clip planes.
*/

#version 330

uniform float osg_FrameTime;
uniform vec4 p3d_TexAlphaOnly;

in vec2 diffuseCoord;
in vec4 vertexColor;
uniform sampler2D p3d_Texture0;

uniform vec4 p3d_ClipPlane[1];
in vec4 vpos;

out vec4 finalColor;

void main() {
	if (dot(p3d_ClipPlane[0], vpos) < 0) {
		float result = dot(p3d_ClipPlane[0], vpos);
		finalColor = vec4(result, 0.0, 0.0, 1.0);
	} else {
		finalColor = texture(p3d_Texture0, diffuseCoord) * vertexColor;
	}
}
