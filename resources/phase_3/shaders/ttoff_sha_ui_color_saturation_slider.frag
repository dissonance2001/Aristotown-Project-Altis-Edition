// Make A Toon Desaturation Slider
// drewcification 110620

// We can't really do this in panda, so we can do some simple math

#version 130
uniform sampler2D p3d_Texture0;

// matColor is (hue, value)
uniform vec2 matColor;
in vec2 texcoord;
out vec4 color;

// rgb to hsv
// we cant just use a desaturate function since it ends up being very inaccurate
// this is the same method used to color the toon itself, so its accurate
vec3 hsv2rgb(vec3 color)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(color.xxx + K.xyz) * 6.0 - K.www);
    return color.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), color.y);
}

void main() {
	// The texture includes the saturation from 0-1
	vec4 saturation = texture(p3d_Texture0, texcoord);
	
	// do the maTH
	color = vec4(hsv2rgb(vec3(matColor.x, saturation.x, matColor.y)), saturation.a);
}