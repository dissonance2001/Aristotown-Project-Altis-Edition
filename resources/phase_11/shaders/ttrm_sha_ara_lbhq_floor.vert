// Reflective LBHQ Floor Vertex Shader
// Drewcification 022624

#version 130
in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

in vec4 transform_weight;
in uvec4 transform_index;

uniform mat4 p3d_ModelViewProjectionMatrix;

uniform mat4 p3d_TransformTable[100];

out vec4 vColor;
out vec2 texcoord;
out vec4 refltexcoord;

void main() {

	gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

	vColor = p3d_Color;
	texcoord = p3d_MultiTexCoord0;

	mat4 proj_adjust_mat = mat4(
		0.5, 0.0, 0.0, 0.0,
		0.0, 0.5, 0.0, 0.0,
		0.0, 0.0, 0.5, 0.0,
		0.5, 0.5, 0.5, 1.0
	);

	vec4 pos = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	refltexcoord = proj_adjust_mat * pos;

}