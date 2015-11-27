import numpy as np
from Shaders import *
import Texture
import OpenGL.GL as gl
import os,sys

print "Constructing opticalDepths"
N = 256 
Re = 6360e3
Ra = 6420e3
Hr = 8e3
Hm = 1.2e3

if not os.path.exists('opdepth.npy'):
  opdepth = np.zeros((N*16,N,4),dtype=np.float32)

  for j,theta in enumerate(np.arange(0,np.pi*0.75,np.pi*0.75/N)):
    print j
    for k,altitudeP in enumerate(np.arange(Re,Ra,(Ra-Re)/(N*16))):
      altitude = Re + ((altitudeP-Re)/(Ra-Re))**3*(Ra-Re)
      P = altitude * np.array([np.sin(theta), np.cos(theta)])
      #P = altitude * np.array([(1-costheta**2)**0.5, costheta])
      if np.cos(theta)<0:
      #if costheta<0:
        if (P[0] < Re):
          opdepth[k][j] = [-1,-1,0,0]
          continue
      r = (Ra**2-P[0]**2)**0.5-P[1]
      nn = 100
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

data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
  
shader = getShader('sky')
renderID = shader.setData(data,indices)
def display(colorTexture,depthTexture):
  gl.glDisable(gl.GL_DEPTH_TEST)
  gl.glDepthMask(False)
  depthTexture.load()
  colorTexture.load()
  opticalDepthmap.load()
  shader.load()
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['colormap'] = Texture.COLORMAP_NUM
  shader['depthmap'] = Texture.DEPTHMAP_NUM
  shader['opticaldepthmap'] = Texture.BUMPMAP_NUM
  shader.draw(gl.GL_TRIANGLES,renderID,1)
  gl.glEnable(gl.GL_DEPTH_TEST)
  gl.glDepthMask(True)
