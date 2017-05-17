import numpy as np
from Shaders import *
import OpenGL.GL.framebufferobjects as glfbo
import Texture
import OpenGL.GL as gl
import os,sys
import logging
import noiseG
import args

N = 256
Re = 6.360e6
Ra = 6.420e6
Hr = 8e3
Hm = 1.2e3

if not os.path.exists('opdepth.npy') or args.args.remake_sky:
  logging.info("Constructing optical depths")
  opdepth = np.zeros((N*16,N,4),dtype=np.float32)

  for j,theta in enumerate(np.arange(0, np.pi*0.75, np.pi*0.75/N)):
    sys.stdout.write('{}/{}\r'.format(j,N))
    sys.stdout.flush()
    for k,altitudeP in enumerate(np.arange(0,1,1./(N*16))):
      altitude = Re + (altitudeP)**3*(Ra-Re)
      P = altitude * np.array([np.sin(theta), np.cos(theta)])
      if np.cos(theta)<0:
        if (P[0] <= Re):
          opdepth[k][j] = [-1,-1,0,0]
      r = (Ra**2-P[0]**2)**0.5-P[1]
      nn = 400
      dx = r/nn
      heights = (P[0]**2+(P[1]+np.arange(0,r,dx))**2)**0.5-Re
      opdepthR = sum(np.exp(-heights/Hr))*dx
      opdepthM = sum(np.exp(-heights/Hm))*dx

      opdepth[k][j] = [opdepthR,opdepthM,0,0]
  np.save('opdepth.npy',opdepth)
else:
  opdepth = np.load('opdepth.npy')

opticalDepthmap = Texture.Texture(Texture.OPTICAL_DEPTHMAP)
opticalDepthmap.load()
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
opticalDepthmap.loadData(opdepth, height=N*16, width=N)
del opdepth

data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

print "Constructing Night Sky"
nightSkyTexture = Texture.Texture(Texture.NIGHTSKY)
if not os.path.exists('nightSky.npy'):
  framebuffer = gl.glGenFramebuffers(1)
  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,framebuffer)
  texSize = 2048
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
  print "=="*20
  for i in xrange(len(stars)/200):
    if (i%(len(stars)/4000)==0):
      print '*',
    shader['starPositions'] = stars[200*i:200*(i+1)]
    gl.glViewport(0,0,texSize,texSize)
    shader['hemisphere'] = 1
    shader.draw(gl.GL_TRIANGLES,nightId,1)
    shader['hemisphere'] = -1
    gl.glViewport(texSize,0,texSize,texSize)
    shader.draw(gl.GL_TRIANGLES,nightId,1)
  print
  gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA);
  nightSkyTexture.saveToFile('nightSky.npy')
else:
  nightSkyTexture.loadFromFile('nightSky.npy')

logging.info("Loading Earth texture")
earthTexture = Texture.Texture(Texture.EARTHMAP)
earthTexture.loadFromImage('assets/earthmap.ppm')
earthTexture.load()

shader = getShader('sky',forceReload  = True)
shader['colormap']        = Texture.COLORMAP_NUM
shader['depthmap']        = Texture.DEPTHMAP_NUM
shader['nightSkymap']     = Texture.NIGHTSKY_NUM
shader['earthMap']        = Texture.EARTHMAP_NUM
shader['opticaldepthmap'] = Texture.OPTICAL_DEPTHMAP_NUM
shader['Re'] = Re
shader['Ra'] = Ra
shader['Hr'] = Hr
shader['Hm'] = Hm
shader['shadowTexture3'] = Texture.SHADOWS3_NUM
renderID = shader.setData(data,indices)

def display(previousStage):
  previousStage.displayColorTexture.load()
  # TODO Is this needed?
  previousStage.displayDepthTexture.load()
  shader.load()
  noiseG.noiseT.load()
  shader.draw(gl.GL_TRIANGLES,renderID,1)
