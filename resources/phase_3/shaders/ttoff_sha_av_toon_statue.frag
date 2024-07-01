// Hardware Skinning Toon Statue for Toontown Central SafeZone Activity
// Drewcification 060321

#version 130

uniform vec4 p3d_ColorScale;

in vec4 vColor;
in vec2 texcoord;

out vec4 color;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;


// Adjust Saturation formula
vec3 adjustSaturation(vec3 color, float adjustment)
{
    const vec3 W = vec3(0.2125, 0.7154, 0.0721);
    vec3 intensity = vec3(dot(color, W));
    return mix(intensity, color, adjustment);
}
void main() {
	// Mix the Texture, ColorScale, and VertexColor to get the full color color
	color = p3d_ColorScale * texture(p3d_Texture0, texcoord)* texture(p3d_Texture1, texcoord) * vColor;
	color.rgb*=1.4;
	// Run the saturation adjust formula
	color = vec4(adjustSaturation(color.rgb, 0.0), color.a);
	color.rgb *= vec3(1.0, 0.937, 0.862);
	
	if (color.a < 0.05) {
        discard;
    }
}