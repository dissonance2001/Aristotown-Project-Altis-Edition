// Make A Toon Hue Color Wheel
// drewcification 110920

// We can't really do this in panda, so we can do some simple math

#version 130
uniform sampler2D p3d_Texture0;

// matColor is (saturation, value)
uniform vec2 matColor;
in vec2 texcoord;
out vec4 color;

// hsv <-> rgb conversions

// we want to do things exactly how it is applied to the toon, so we use this code
// it aint pretty, but it is VERY accurate
vec3 hsv2rgb(vec3 color)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(color.xxx + K.xyz) * 6.0 - K.www);
    return color.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), color.y);
}

vec3 rgb2hsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

void main() {
	// The texture includes the hue in rgba
	vec4 wheeltexture = texture(p3d_Texture0, texcoord);
	vec3 hsv =rgb2hsv(wheeltexture.xyz);
	float hue = hsv.x;
	
	// the border of the circle should stay black. if we don't do this
	// it sets it as red because the value isn't retained
	if (hsv.z == 0) {
		color = wheeltexture;
	}
	else{
		color = vec4(hsv2rgb(vec3(hue, matColor.x, matColor.y)), wheeltexture.a);
	}
}