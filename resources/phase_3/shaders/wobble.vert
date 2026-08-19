#version 330

uniform float speed;
uniform float waves;
uniform float power;

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
  
  vertexPosition.x += sin((osg_FrameTime * speed) + (vertexPosition.y * waves)) * power;

  gl_Position = p3d_ProjectionMatrix * vertexPosition;
}