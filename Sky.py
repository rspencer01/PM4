import numpy as np
from Shaders import *
import OpenGL.GL.framebufferobjects as glfbo
import Texture
import OpenGL.GL as gl
import os,sys
import noiseG
import args

print "Constructing opticalDepths"
N = 256
Re = 6.360e6
Ra = 6520e3
Hr = 1e4
Hm = 1.15e3

if not os.path.exists('opdepth.npy') or args.args.remake_sky:
  opdepth = np.zeros((N*16,N,4),dtype=np.float32)

  for j,theta in enumerate(np.arange(0,np.pi*0.75,np.pi*0.75/N)):
    for k,altitudeP in enumerate(np.arange(Re,Ra,(Ra-Re)/(N*16))):
      altitude = Re + ((altitudeP-Re)/(Ra-Re))**3*(Ra-Re)
      P = altitude * np.array([np.sin(theta), np.cos(theta)])
      #P = altitude * np.array([(1-costheta**2)**0.5, costheta])
      if np.cos(theta)<0:
      #if costheta<0:
        if (P[0] <= Re):
          opdepth[k][j] = [-1,-1,0,0]
      #    continue
      r = (Ra**2-P[0]**2)**0.5-P[1]
      nn = 400
      dx = r/nn
      opdepthR = 0;
      opdepthM = 0;
     # for lam in np.arange(0,r,dx):
      ints = (P[0]**2+(P[1]+np.arange(0,r,dx))**2)**0.5-Re
      opdepthR = sum(np.exp(-ints/Hr))*dx
      opdepthM = sum(np.exp(-ints/Hm))*dx

      opdepth[k][j] = [opdepthR,opdepthM,0,0]
  np.save('opdepth.npy',opdepth)
else:
  opdepth = np.load('opdepth.npy')

opticalDepthmap = Texture.Texture(Texture.BUMPMAP)
opticalDepthmap.load()
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
opticalDepthmap.loadData(N,N,opdepth)
del opdepth

data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)

print "Constructing Night Sky"
nightSkyTexture = Texture.Texture(Texture.COLORMAP2)
if not os.path.exists('nightSky.npy'):
  framebuffer = gl.glGenFramebuffers(1)
  gl.glBindFramebuffer(gl.GL_FRAMEBUFFER,framebuffer)
  texSize = 2048
  nightSkyTexture.loadData(2*texSize,texSize,None)

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
  nightSkyTexture.loadData(2*texSize,texSize,None)

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

shader = getShader('sky',forceReload=True)
renderID = shader.setData(data,indices)
def display(previousStage):
  #gl.glDisable(gl.GL_DEPTH_TEST)
  #gl.glDepthMask(False)
  previousStage.displayColorTexture.load()
  # TODO Is this needed?
  previousStage.displayDepthTexture.load()
  nightSkyTexture.load();
  opticalDepthmap.load()
  shader.load()
  noiseG.noiseT.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['colormap'] = Texture.COLORMAP_NUM
  shader['noisemap'] = Texture.NOISE_NUM
  shader['depthmap'] = Texture.DEPTHMAP_NUM
  shader['nightSkymap'] = Texture.COLORMAP2_NUM
  shader['opticaldepthmap'] = Texture.BUMPMAP_NUM
  shader.draw(gl.GL_TRIANGLES,renderID,1)
  #gl.glEnable(gl.GL_DEPTH_TEST)
  #gl.glDepthMask(True)
