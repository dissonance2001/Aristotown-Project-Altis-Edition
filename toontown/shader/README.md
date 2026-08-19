# Shader Module #

## Breakdown

### base.tsm
ToontownShaderManager will always be initialized on startup and accessible via ``base.tsm``.
When ToontownShaderManager is initialized, two FilterManagers are created. One is for render and the other for render2d (GUI).
It is technically possible to apply a shader on only one filtermanager but not the other. It is also technically possible to apply two *different* shaders at the same time,
one shader for ``manager`` and the other for ``manager2d``.

### base.lutman
The LUTManager is only initialized when called to be. As of right now, while the LUT Manager can fall under ``base.shader``, it's special
right now and has its own object. (This can be refactored to use base.shader instead sometime)

### base.shader
Any other shader that is initialized will be accessible using base.shader. Keep in mind that you can only
have one shader active at any time on a given FilterManager.


## How to add Shaders

Each type of shader is defined individually as a class.  You can find a template shader file to base your shader off with ``TemplateShader.py``

Once the shader class has been created, you can add an init function in ToontownShaderManager so that a new instance can be passed through using the same FilterManager.

Example:

```python
def initFilmGrain(self, parent):
    from . import FilmGrainShader as fgs
    return fgs.FilmGrainShader(parent, self.manager)
```


Due to deprecating Cg shaders, you can *only* utilize GLSL shaders. There is a script located at ``tools/cg2glsl.py`` that may assist you in conversion.

If you decide to add a frag shader that requires a custom input such as ``colorTexture`` and ``enabled`` on the chromatic aberration shader, you would need to pass the values through using ``setShaderInput``

``` glsl
uniform sampler2D colorTexture;

uniform vec2 enabled;
```

``` python
colortex = Texture()
self.enabled = True
...
self.quad.setShaderInput("colorTexture", colortex)
self.quad.setShaderInput("enabled", (self.enabled, self.enabled))
```

## Implementing the Shader Manager
ToontownShaderManager, or ``base.tsm``, is the parent class for any Shader object, including LUTManager (``base.lutman``) and ``base.shader`` objects.

In order to instantiate a shader, you just need to call base.tsm: ~~& change the value of the CR variable respectfully~~:

```
dls = base.tsm.initDialation(base.aspect2d)
base.cr.DLSEnabled = True
```

(self-note: i dont think we need base.cr variables anymore but they still exist)

Currently, the recommended way to initialize a shader is to create and call the respected method in ToonBase. Here's a sample of how a shader is initalized:
```python
    def initFilmGrainFilter(self):
        if base.shader is not None:
            base.shader.removeShader()
        if base.tsm is not None:
            return base.tsm.initFilmGrain(aspect2d)
```
Remember that we can only have one instance of a shader at any given time, so we must destroy base.shader to replace it with the incoming shader object.

Since the init methods currently return the shader object, it's important that you re-assign base.shader: ``base.shader = base.initFilmGrainFilter()`` (this can probably be optimized but ye)


## Limitations
At the moment, there isn't any support for stackable shaders without concatenating two shaders into one.

## Bugs / TODO
- Show/hide shaders without necessarily trying to destroy them (LUTManager is fine)
- Make sure there aren't any memory leaks from not cleaning everything up properly
- We don't need aspect2d/parent, remove it
- Probably wanna migrate lutman to use base.shader instead

## Resources
- [List of Panda3D GLSL inputs](https://docs.panda3d.org/1.10/python/programming/shaders/list-of-glsl-inputs)
- [Game Shaders for Beginners (uses Panda3D)](https://github.com/lettier/3d-game-shaders-for-beginners)

