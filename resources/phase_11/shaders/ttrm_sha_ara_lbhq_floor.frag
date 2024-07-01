// Reflective LBHQ Floor Fragment Shader
// Drewcification 022624

#version 130

uniform vec4 p3d_ColorScale;

in vec4 vColor;
in vec2 texcoord;
in vec4 refltexcoord;

out vec4 color;

uniform float osg_FrameTime;
uniform sampler2D p3d_Texture0;
uniform sampler2D refl_texture;

void main() {
	// Mix the Texture, ColorScale, and VertexColor to get the full color color
	color = p3d_ColorScale * texture(p3d_Texture0, texcoord) * vColor;

    // default the transparency of the floor to be fully opaque, we dont need to see the underground geometry with realtime reflection
    color.a = 1.0;

    vec2 proj_uv = refltexcoord.xy / refltexcoord.w;

    vec4 refl_tex = texture(refl_texture, proj_uv);
    color += refl_tex*.1;
    //color = mix(color, refl_tex, clamp(refl_tex.a, 0.0, 0.1));
	if (color.a < 0.1) {
        discard;
    }
}