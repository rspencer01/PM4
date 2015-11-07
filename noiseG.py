import numpy as np
from Shaders import *
import OpenGL.GL as gl
import Texture
import noise

RELOAD =  False

print "Constructing Noise"

noiseT = Texture.Texture(Texture.NOISE)
textWidth = 800
textHeight = textWidth
if RELOAD:
  d = np.zeros((textWidth,textHeight,4),dtype=np.float32)
  # How many units?
  dx = 5
  dy = 5
  for i in range(textWidth):
    for j in range(textHeight):
      s = float(i)/textWidth
      t = float(j)/textHeight
      x1 = 1
      y1 = 1
      nx = x1+np.cos(s*2*np.pi)*dx/(2*np.pi)
      ny = y1+np.cos(t*2*np.pi)*dx/(2*np.pi)
      nz = x1+np.sin(s*2*np.pi)*dx/(2*np.pi)
      nw = y1+np.sin(t*2*np.pi)*dx/(2*np.pi)

      t = noise.snoise4(nx,ny,nz,nw,octaves=10,persistence=0.6)
#      t += noise.snoise4(nx/30,ny/30,nz/30,nw/30,octaves=3)*1
 #     t= np.sin(s*2*np.pi)/4+np.cos(t*2*np.pi)/4
      d[i,j] = (t,t,t,t)
  for i in range(textWidth):
    for j in range(textHeight):
      v1= np.array([float(i)/textWidth*200, d[i,j][3]   ,float(j)/textWidth*200]) 
      v2= np.array([float(i+1)/textWidth*200, d[(i+1)%textWidth,j][3] ,float(j)/textWidth*200]) 
      v3= np.array([float(i)/textWidth*200, d[i,(j+1)%textHeight][3] ,float(j+1)/textWidth*200]) 
      d[i,j][:3] = np.cross(v3-v1,v2-v1)
      d[i,j][:3] /= np.dot(d[i,j][:3],d[i,j][:3])**0.5
  np.save('noise.npy',d)
else:
  d=np.load('noise.npy')
  
noiseT.loadData(d.shape[0],d.shape[1],d)
noiseT.load()

def load(setUniform):
  noiseT.load()
  setUniform('noise',Texture.NOISE_NUM)
  
  

