// Generic UI Shader
// drewcification 110620

// Theres basically no reason vertex data would need to be
// modified for a ui element, so this will be used
#version 130

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;

out vec4 vColor;
out vec2 texcoord;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  vColor = p3d_Color;
  texcoord = p3d_MultiTexCoord0;
}