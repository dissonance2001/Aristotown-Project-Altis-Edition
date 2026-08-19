/*
  Passthrough fragment shader.
  Whipped up by Main.
  Buy him a pizza so that we can get 1.3!
*/

#version 330

uniform float osg_FrameTime;
uniform vec4 p3d_TexAlphaOnly;

in vec2 diffuseCoord;
in vec4 vertexColor;
uniform sampler2D p3d_Texture0;

out vec4 finalColor;

void main() {
    finalColor = texture(p3d_Texture0, diffuseCoord) * vertexColor;
}
