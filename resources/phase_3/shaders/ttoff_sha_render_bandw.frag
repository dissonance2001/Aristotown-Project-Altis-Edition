// Render Desaturate | Fragment
// drewcification 092520
#version 130

uniform sampler2D p3d_Texture0;

uniform vec4 p3d_TexAlphaOnly;
uniform float osg_FrameTime;
uniform vec4 p3d_ColorScale;
in vec4 vColor;
in vec2 texcoord;
out vec4 color;

// Adjust Saturation formula
vec3 adjustSaturation(vec3 color, float adjustment)
{
    const vec3 W = vec3(0.2125, 0.7154, 0.0721);
    vec3 intensity = vec3(dot(color, W));
    return mix(intensity, color, adjustment);
}

void main() {
	// workaround to fix black text rendering
	vec4 texColor = texture(p3d_Texture0, texcoord) + p3d_TexAlphaOnly;
	
	
	// Mix the Texture, ColorScale, and VertexColor to get the true regular color
	color = p3d_ColorScale * texColor * vColor;

	// Run the saturation adjust formula
	color = vec4(adjustSaturation(color.rgb, 0.0), color.a);

	// Calculate some noise based on the frame time
	float noise = fract(10000 * sin((gl_FragCoord.x + gl_FragCoord.y * osg_FrameTime) * 3.14/180));

	// Add the noise
	color.rgb += 0.2*noise;
}
