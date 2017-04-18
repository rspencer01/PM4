import OpenGL.GL as gl
import numpy as np
import Shaders
import Texture
import OpenGL.GL.framebufferobjects as glfbo

vertexData = np.zeros(4,dtype=[("position" , np.float32,3)])
vertexData['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

highColorShader = Shaders.getShader('highColor',forceReload=True)
highColorRenderID = highColorShader.setData(vertexData,indices)
highColorFBO = gl.glGenFramebuffers(1)
highColorDepth = Texture.Texture(Texture.DEPTHMAP)
highColorDepth.load()
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)    
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_FUNC,gl.GL_LEQUAL)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_MODE,gl.GL_NONE)
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, 1, 1, 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)

def extractHighColor(inputTexture,threshhold,outputTexture):
  otyp = outputTexture.textureType
  ityp = inputTexture.textureType

  inputTexture.textureType = Texture.COLORMAP 

  size = inputTexture.size

  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, highColorFBO)
  outputTexture.load()
  outputTexture.loadData(size[0],size[1],None)
  highColorDepth.load()
  gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, size[0], size[1], 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)
  gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, highColorDepth.id, 0)
  gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0, outputTexture.id, 0);
  gl.glDrawBuffers(1,[gl.GL_COLOR_ATTACHMENT0])
  glfbo.checkFramebufferStatus()
  gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

  highColorShader.load()
  highColorShader['inTex'] = Texture.COLORMAP_NUM
  highColorShader['threshhold'] = float(threshhold)
  inputTexture.load() 
  highColorShader.draw(gl.GL_TRIANGLES,highColorRenderID)

  outputTexture.textureType = otyp
  inputTexture.textureType = ityp


gaussianShader = Shaders.getShader('gaussian',forceReload=True)
gaussianRenderID = gaussianShader.setData(vertexData,indices)
gaussianFBO = gl.glGenFramebuffers(1)
gaussianDepth = Texture.Texture(Texture.DEPTHMAP)
gaussianDepth.load()
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)    
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_FUNC,gl.GL_LEQUAL)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_COMPARE_MODE,gl.GL_NONE)
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, 1, 1, 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)

def gaussianBlur(inputTexture,radius,outputTexture):
  otyp = outputTexture.textureType
  ityp = inputTexture.textureType

  inputTexture.textureType = Texture.COLORMAP 

  size = inputTexture.size

  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, gaussianFBO)
  outputTexture.load()
  outputTexture.loadData(size[0],size[1],None)
  gaussianDepth.load()
  gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,gl.GL_DEPTH_COMPONENT32, size[0], size[1], 0,gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, None)
  gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gaussianDepth.id, 0)
  gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0, outputTexture.id, 0);
  gl.glDrawBuffers(1,[gl.GL_COLOR_ATTACHMENT0])
  glfbo.checkFramebufferStatus()
  gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

  gaussianShader.load()
  gaussianShader['inTex'] = Texture.COLORMAP_NUM
  gaussianShader['radius'] = float(radius)
  inputTexture.load() 
  gaussianShader.draw(gl.GL_TRIANGLES,gaussianRenderID)

  outputTexture.textureType = otyp
  inputTexture.textureType = ityp
