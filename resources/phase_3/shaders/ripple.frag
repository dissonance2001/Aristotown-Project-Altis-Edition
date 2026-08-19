#version 330

uniform float vscroll;
uniform float chevron_depth;
uniform float uv_xoffset;

uniform float osg_FrameTime;
uniform vec4 p3d_TexAlphaOnly;

in vec2 diffuseCoord;
in vec4 vertexColor;
uniform sampler2D p3d_Texture0;

out vec4 finalColor;

void main() {
	// Calculate a yoffset.
	float yoffset = vscroll * osg_FrameTime;
	yoffset -= abs(diffuseCoord.x - uv_xoffset) * chevron_depth;
	
	// Apply the coord.
	vec2 realCoord = diffuseCoord + vec2(0.0, yoffset);
    finalColor = texture(p3d_Texture0, realCoord) * vertexColor;
	// finalColor = vec4(mod(realCoord.x, 1.0), mod(realCoord.y, 1.0), 0.0, 1.0);
}
