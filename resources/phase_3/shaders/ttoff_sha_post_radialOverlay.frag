// Radial Menu Blur | Frag
// drewcification 021622
// adapted from https://www.shadertoy.com/view/ltScRG
#version 130

// These 3 are required by the filter manager to be present
uniform sampler2D color_texture;
uniform sampler2D depth_texture;
uniform vec2 resolution;

uniform float osg_FrameTime;

in vec2 texcoord;
out vec4 color;
const int samples = 8;

const float sigma = float(samples) * .25;

float gaussain(vec2 i){
	return exp(-0.5 * dot(i/=sigma, i)) / (6.28 * sigma*sigma);
}

void main() {
	color = vec4(0);
	for (int i = 0; i< samples*samples; i++){
		vec2 d = vec2(i%int(samples), i/int(samples)) * 1 - samples/2.;
		color += gaussain(d) * texture(color_texture, texcoord + 1./resolution.xy * d);
	}
}
