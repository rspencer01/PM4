import numpy as np
import logging
from Shaders import *
import OpenGL.GL as gl
import Texture
import noise
import os
import args

logging.info("Constructing Noise")

noiseT = Texture.Texture(Texture.NOISE)
textWidth = 1000
textHeight = textWidth
if not os.path.exists('noise.npy') or args.args.remake_noise:
  logging.info(" + Creating texture")
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
      ny = y1+np.cos(t*2*np.pi)*dy/(2*np.pi)
      nz = x1+np.sin(s*2*np.pi)*dx/(2*np.pi)
      nw = y1+np.sin(t*2*np.pi)*dy/(2*np.pi)

      t = noise.snoise4(nx,ny,nz,nw,octaves=7,persistence=0.5)
      d[i,j] = (t,t,t,t)
  for i in range(textWidth):
    for j in range(textHeight):
      v1= np.array([dx*float(i)/textWidth,   d[i,j][3],                dy*float(j)/textWidth])
      v2= np.array([dx*float(i+1)/textWidth, d[(i+1)%textWidth,j][3],  dy*float(j)/textWidth])
      v3= np.array([dx*float(i)/textWidth,   d[i,(j+1)%textHeight][3], dy*float(j+1)/textWidth])
      d[i,j][:3] = np.cross(v3-v1,v2-v1)
      d[i,j][:3] /= np.dot(d[i,j][:3],d[i,j][:3])**0.5

      d[i,j,2] = (d[(i+1)%textWidth,j,3] - d[i,j,3] )/ (1. / textWidth)
      d[i,j,0] = (d[i,(j+1)%textWidth,3] - d[i,j,3] )/ (1. / textHeight)
  np.save('noise.npy',d)
else:
  logging.info(" + Loaded from file")
  d=np.load('noise.npy')

logging.info(" + Uploading texture to GPU")
noiseT.loadData(d.shape[0],d.shape[1],d)
noiseT.load()

def load(setUniform):
  noiseT.load()
  setUniform('noise',Texture.NOISE_NUM)

def get(x,y):
  return d[int(d.shape[0]*x)][int(d.shape[1]*y)]
