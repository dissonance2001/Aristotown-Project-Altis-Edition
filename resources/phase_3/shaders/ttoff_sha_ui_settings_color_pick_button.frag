// Color Picker Button
// drewcification 040721

// this is the little icon, this shader just ensures the black border always stays, even if the transparency is lowered
// this can look a little weird, but its probably just my placeholder textures
#version 130

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

in vec4 vColor;
in vec2 texcoord;
out vec4 color;

void main() {
    vec4 texColor = texture(p3d_Texture0, texcoord);

    // Mix the Picked Color with the background.
    // The 1-texColor.r ensures this only gets applied to areas that are white on the base texture
    // so we keep the border untouched
    color = mix(vColor * texColor, texColor, 1-texColor.r);

    // Keep a small stripe of the color opaque
    if (texcoord.y < 0.82){
            color.a = texColor.a;
    }
}
