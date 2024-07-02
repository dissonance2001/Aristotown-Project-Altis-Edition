// Prop Generator - Collision Generator Effect
// Drewcification 090921

#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

out vec2 texcoord;
out float cameraDist;

void main() {
	gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	cameraDist = length((p3d_ModelViewMatrix * p3d_Vertex).xyz);
	texcoord = p3d_MultiTexCoord0;
}