// Prop Generator - Collision Generator Effect
// Drewcification 090921

#version 130

uniform vec4 p3d_ColorScale;

in float cameraDist;
in vec2 texcoord;

out vec4 color;

uniform sampler2D p3d_Texture0;
uniform float osg_FrameTime;
uniform bool forceVisible;
uniform bool forceHide;

void main() {
	float dist = cameraDist / 20.0;	vec2 tc = texcoord * 2;	tc.xy -= osg_FrameTime / 10.0; color = texture(p3d_Texture0, tc).rrra * p3d_ColorScale;
		
	if(forceVisible){dist = 0.0;}else{if (forceHide){discard;}}if (dist > 1.0){discard;}if (color.a < 0.1){discard;}
	if (dist != 0.0){color.a = 1.0 - dist;}
}