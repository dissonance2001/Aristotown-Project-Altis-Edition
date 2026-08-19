#version 330

uniform float hscroll;
uniform float vscroll;
uniform float frequency;
uniform float amplitude;

uniform float osg_FrameTime;
uniform vec4 p3d_TexAlphaOnly;

in vec2 diffuseCoord;
in vec4 vertexColor;
uniform sampler2D p3d_Texture0;

out vec4 finalColor;

void main() {
	// Calculate an xoffset.
	float xoffset = sin(diffuseCoord.y * frequency) * amplitude;
	xoffset += hscroll * osg_FrameTime;
	
	// Calculate a yoffset.
	float yoffset = vscroll * osg_FrameTime;
	
	// Apply the coord.
	vec2 realCoord = diffuseCoord + vec2(xoffset, yoffset);
    finalColor = texture(p3d_Texture0, realCoord) * vertexColor;
}
