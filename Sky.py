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

shader = getShader('sky')
shader['colormap']        = Texture.COLORMAP_NUM
shader['depthmap']        = Texture.DEPTHMAP_NUM
shader['opticaldepthmap'] = Texture.OPTICAL_DEPTHMAP_NUM
shader['shadowTexture3'] = Texture.SHADOWS3_NUM
renderID = shader.setData(data,indices)

def display(previousStage):
  previousStage.displayColorTexture.load()
  # TODO Is this needed?
  previousStage.displayDepthTexture.load()
  optical_depth_render_stage.displayColorTexture.loadAs(Texture.OPTICAL_DEPTHMAP)
  shader.load()
  shader.draw(gl.GL_TRIANGLES,renderID,1)
