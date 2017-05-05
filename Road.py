from noise import *
import numpy as np
import Texture
import OpenGL.GL as gl
import Shaders
import Terrain

roadData = 'road.npy'
print "Generating road"

Reload = os.path.isfile(roadData)

bumpmap = Texture.Texture(Texture.BUMPMAP)

roadWidth = 4

sz = 500

def round(v):
  nv = np.zeros((sz,sz,3))
  eps = 3
  for i in range(sz-1):  
    for j in range(sz-1):
      if v[i,j-1][0]>eps and v[i-1,j][0] > eps and v[i+1,j][0] > eps and v[i,j+1][0]>eps:
        nv[i,j] = v[i,j]
  return nv
  
def rem(x):
  return x-int(x)
def rndshape(t,a=False,b=True):
  if b:
    t+=0.5
  t = rem(t)
  
  if (a):
    if t<0.9:
      ans= (1.0-((t-0.45)/0.45)**2)**0.5
    else:
      ans= -(1.0-((0.95-t)/0.05)**2)**0.5
    
  else:
    if t<0.5:
      ans= (1.0-((t-0.25)/0.25)**2)**0.5
    else:
      ans= -(1.0-((0.75-t)/0.25)**2)**0.5
  if b:
    ans *=-1
  return ans
 
if Reload:
  data = np.zeros((sz,sz,4),dtype=np.float32)
  a = 4
  b = 7
  for i in range(sz):  
    for j in range(sz):
    
      a = (1+ i/float(sz) + 0.1*pnoise2(7+2*i/float(sz),9+2*j/float(sz)))/1.6
      b = (1+ j/float(sz) + 0.1*pnoise2(2+5*i/float(sz),2*j/float(sz)))/1.6
     # x = (np.sin(a*3.141592*4) + np.sin(b*3.141592*10))/2
      x = (rndshape(a*8,True,rem(b*12)>0.5) + rndshape(b*12))/2 
      
      x += snoise2(float(j)/sz*5,float(i)/sz*5,octaves=2,persistence=0.5)*0.3
      
      
      
      x = abs(x)**1.2
      x = max(0,x-0.5)
      x = abs(x)**0.8 * 0.2-0.09
      if x>0:
        x = x**0.3 * 0.2
      
      
      data[j,i] = np.float32(np.array([x,x,x,x]))
  st = []
  print "Culling edges"
  for i in range(sz):
    st.append([0,i])
    st.append([i,0])
    st.append([sz-1,i])
    st.append([i,sz-1])
  while len(st)>0:
    c = st[-1]
    st = st[:-1]
    if data[c[0],c[1]][3]<0.01:
      continue
    if c[0]>0:
      st.append((c[0]-1,c[1]))
    if c[0]<sz-1:
      st.append((c[0]+1,c[1]))
    if c[1]>0:
      st.append((c[0],c[1]-1))
    if c[1]<sz-1:
      st.append((c[0],c[1]+1))
    data[c[0],c[1]] = (-1,-1,-1,-1)
    

  for i in range(sz):
    for j in range(sz):
      v1= np.array([float(i)/sz*roadWidth   , data[i,j][3]   , float(j)/sz*roadWidth]) 
      if i<sz-1:
        v2= np.array([float(i+1)/sz*roadWidth , data[i+1,j][3] , float(j)/sz*roadWidth]) 
      else:
        v2= np.array([float(i-1)/sz*roadWidth , data[i-1,j][3] , float(j)/sz*roadWidth]) 
      if j<sz-1:
        v3= np.array([float(i)/sz*roadWidth , data[i,j+1][3] , float(j+1)/sz*roadWidth]) 
      else:
        v3= np.array([float(i)/sz*roadWidth , data[i,j-1][3] , float(j-1)/sz*roadWidth]) 
      data[i,j][:3] = np.cross(v3-v1,v2-v1)
  np.save('road.npy',data)
else:
  data=np.load(roadData)
    

bumpmap.load()
bumpmap.loadData(data)

path = [np.array((6*i,0,snoise2(float(i)/10,0.2))) for i in range(100)]
data = np.zeros((len(path)-1)*6,dtype=[("position" , np.float32,3),("uv" , np.float32,2)])
c = 0
for i in range(len(path)-1):
  norm = np.array((0,0,2))
  data['position'][c] = path[i]-norm
  data['uv'][c] = (0,0)
  c += 1
  data['position'][c] = path[i]+norm
  data['uv'][c] = (1,0)
  c += 1
  data['position'][c] = path[i+1]-norm
  data['uv'][c] = (0,1)
  c += 1
  data['position'][c] = path[i]+norm
  data['uv'][c] = (1,0)
  c += 1
  data['position'][c] = path[i+1]-norm
  data['uv'][c] = (0,1)
  c += 1
  data['position'][c] = path[i+1]+norm
  data['uv'][c] = (1,1)
  c += 1
  
    

I = []
indices = np.array(I,dtype=np.int32)
shader = Shaders.getShader('road',True)
renderID = shader.setData(data,indices)
def display():
  shader['model'] = np.eye(4,dtype=np.float32)
  shader['bumpmap'] = Texture.BUMPMAP_NUM
  shader.draw((len(path)-1)*6,renderID)
