#version 330

uniform float amt;

uniform float osg_FrameTime;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;

in vec2 p3d_MultiTexCoord0;
in vec2 p3d_MultiTexCoord1;

out vec4 vertexPosition;
out vec4 vertexColor;
out vec2 normalCoord;
out vec2 diffuseCoord;

void main() {
  vertexColor    = p3d_Color;
  vertexPosition = p3d_ModelViewMatrix * p3d_Vertex;

  normalCoord   = p3d_MultiTexCoord0;
  diffuseCoord  = p3d_MultiTexCoord1;
  
  vec4 op = vertexPosition * amt;
  vertexPosition = vec4(round(op.x) / amt, round(op.y) / amt, round(op.z) / amt, round(op.w) / amt);

  gl_Position = p3d_ProjectionMatrix * vertexPosition;
}