import numpy as np
from Shaders import *
import OpenGL.GL.framebufferobjects as glfbo
import Texture
import OpenGL.GL as gl
import logging
import args
import RenderStage
from configuration import config
import tqdm
import assets

N = config.sky_integration_steps
Re = config.earth_radius
Ra = config.atmosphere_radius

opticalDepthmap = Texture.Texture(Texture.OPTICAL_DEPTHMAP)
opticalDepthmap.load()
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)

data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

logging.info("Precalculating optical depths")
optical_depth_shader = getShader('optical_depths')
optical_depth_render_stage = RenderStage.RenderStage()
optical_depth_render_stage.reshape(2048)
optical_depth_render_stage.load(2048, 2048)
renderID = optical_depth_shader.setData(data, indices)
optical_depth_shader.draw(gl.GL_TRIANGLES,renderID,1)
optical_depth_render_stage.displayColorTexture.loadAs(Texture.OPTICAL_DEPTHMAP)
gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

nightSkyTexture = Texture.Texture(Texture.NIGHTSKY)
def constructNightSky():
  logging.info("Constructing night sky")
  framebuffer = gl.glGenFramebuffers(1)
  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,framebuffer)
  texSize = 1536
  nightSkyTexture.loadData(None, width=2*texSize, height=texSize)

  depthbuffer = gl.glGenRenderbuffers(1)
  gl.glBindRenderbuffer(gl.GL_RENDERBUFFER,depthbuffer)
  gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT,2*texSize,texSize)
  gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, depthbuffer)

  gl.glFramebufferTexture(gl.GL_FRAMEBUFFER,gl.GL_COLOR_ATTACHMENT0,nightSkyTexture.id,0);

  gl.glDrawBuffers(1,[gl.GL_COLOR_ATTACHMENT0])
  glfbo.checkFramebufferStatus()
  shader = getShader('nightSky')
  nightId = shader.setData(data,indices)
  nightSkyTexture.load()
  shader.load()
  gl.glClear(gl.GL_DEPTH_BUFFER_BIT| gl.GL_COLOR_BUFFER_BIT)
  gl.glDisable(gl.GL_DEPTH_TEST)
  nightSkyTexture.loadData(None, width=2*texSize, height=texSize)

  stars = np.loadtxt(open("assets/stars.csv/hygxyz.csv","rb"),delimiter=",",skiprows=1,usecols=(17,18,19,13))
  stars = stars[stars.argsort(0)[:,3]]

  gl.glClear(gl.GL_COLOR_BUFFER_BIT)
  gl.glBlendFunc(gl.GL_ONE,gl.GL_ONE);
  for i in tqdm.trange(len(stars)/200, leave=False):
    shader['starPositions'] = stars[200*i:200*(i+1)]
    gl.glViewport(0,0,texSize,texSize)
    shader['hemisphere'] = 1
    shader.draw(gl.GL_TRIANGLES,nightId,1)
    shader['hemisphere'] = -1
    gl.glViewport(texSize,0,texSize,texSize)
    shader.draw(gl.GL_TRIANGLES,nightId,1)
  gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA);
  return nightSkyTexture.getData()

nightSkyTexture.loadData(assets.getAsset('nightSky', constructNightSky, (), args.args.remake_stars))



shader = getShader('sky')
shader['Re']              = Re
shader['Ra']              = Ra
shader['integrationSteps'] = N
shader['colormap']        = Texture.COLORMAP_NUM
shader['depthmap']        = Texture.DEPTHMAP_NUM
shader['opticaldepthmap'] = Texture.OPTICAL_DEPTHMAP_NUM
shader['nightSkyTexture'] = Texture.NIGHTSKY_NUM
shader['shadowTexture3']  = Texture.SHADOWS3_NUM
renderID = shader.setData(data,indices)

def display(previousStage):
  previousStage.displayColorTexture.load()
  # TODO Is this needed?
  previousStage.displayDepthTexture.load()
  optical_depth_render_stage.displayColorTexture.loadAs(Texture.OPTICAL_DEPTHMAP)
  shader.load()
  shader.draw(gl.GL_TRIANGLES,renderID,1)
