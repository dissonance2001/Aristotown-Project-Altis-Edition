#version 130

uniform sampler2D p3d_Texture0;

uniform vec4 p3d_TexAlphaOnly;
in vec2 texcoord;
out vec4 color;

uniform float osg_FrameTime;

void main() {
	vec4 texColor = texture(p3d_Texture0, texcoord) + p3d_TexAlphaOnly;

	// Mix the Texture, ColorScale, and VertexColor to get the true regular color
	color = texColor;

	float num = 512*1.3;

	vec3 scanlines = vec2(sin(texcoord.y * num), cos(texcoord.y * num)).xyx;

	color.xyz+=color.xyz*scanlines*.3;

	// add a little flicker effect
	color.xyz+=color.xyz*sin(100*osg_FrameTime)*0.04;

}
