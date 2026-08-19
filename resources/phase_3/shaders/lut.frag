//GLSL
#version 330

uniform float wet;
uniform sampler2D lut;

uniform float osg_FrameTime;
uniform vec4 p3d_TexAlphaOnly;

in vec2 diffuseCoord;
in vec4 vertexColor;
uniform sampler2D p3d_Texture0;

out vec4 finalColor;

vec3 applyColorLUT(sampler2D lut, vec3 color) {
    float lutSize = float(textureSize(lut, 0).y);
    color = clamp(color, vec3(0.5 / lutSize), vec3(1.0 - 0.5 / lutSize));
    vec2 texcXY = vec2(color.r * 1.0 / lutSize, 1.0 - color.g);

    int frameZ = int(color.b * lutSize);
    float offsZ = fract(color.b * lutSize);

    vec3 sample1 = textureLod(lut, texcXY + vec2((frameZ) / lutSize, 0), 0).rgb;
    vec3 sample2 = textureLod(lut, texcXY + vec2( (frameZ + 1) / lutSize, 0), 0).rgb;

    return mix(sample1, sample2, offsZ);
}

void main() {
    vec4 color = texture(p3d_Texture0, diffuseCoord) * vertexColor;
	finalColor = vec4(mix(applyColorLUT(lut, color.rgb), color.rgb, 1 - wet), color.a);
}
