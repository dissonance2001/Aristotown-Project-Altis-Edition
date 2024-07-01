// Render wobbly frag
// drewcification 010721
#version 130

uniform sampler2D p3d_Texture0;

uniform vec4 p3d_TexAlphaOnly;
uniform vec4 p3d_ColorScale;
in vec4 vColor;
in vec2 texcoord;
out vec4 color;

uniform float osg_FrameTime;

void main() {
	// workaround to fix black text rendering
	vec4 texColor = texture(p3d_Texture0, texcoord) + p3d_TexAlphaOnly;
	
	
	// Mix the Texture, ColorScale, and VertexColor to get the true regular color
	color = p3d_ColorScale * texColor * vColor;
	// Tint the screen green
	color.r -= 0.2 * ((sin(osg_FrameTime/1.3) + 1) / 2);
	color.b -= 0.2 * ((sin(osg_FrameTime/1.3) + 1) / 2);
}
