from configuration import config
import Pager
import logging
from Shaders import *
import Texture
import RenderStage

pageSize                = config.terrain_page_size
pagesAcross             = 60000 / pageSize
pageResoultion          = config.terrain_page_resolution
numPages                = config.terrain_num_pages
pageMapping             = Pager.Pager(numPages**2)

logging.info("{}m on a side of a page square for a resolution of {}m".format(pageSize, pageSize/pageResoultion))

updateUniversalUniform('pageTable', Texture.PAGE_TABLE_NUM)
updateUniversalUniform('pagedOffsetTexture', Texture.PAGED_TEXTURE_1_NUM)
updateUniversalUniform('pagedNormalTexture', Texture.PAGED_TEXTURE_2_NUM)
updateUniversalUniform('pageSize', pageSize)
updateUniversalUniform('numPages', numPages)

pageTableTexture = Texture.Texture(Texture.PAGE_TABLE)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST_MIPMAP_NEAREST)
pageTableTexture.loadData(np.zeros((1,1,4))-1)

pageRenderStage = RenderStage.RenderStage()
pageRenderStage.reshape(pageResoultion*numPages)
pageNormalTexture = pageRenderStage.displayColorTexture
pageOffsetTexture = pageRenderStage.displayAuxColorTexture

pageTableTexture.loadAs(Texture.PAGE_TABLE)
pageOffsetTexture.loadAs(Texture.PAGED_TEXTURE_1)
pageNormalTexture.loadAs(Texture.PAGED_TEXTURE_2)

pagingShader = getShader('pagingShader', forceReload=True)
pagingShader['pageSize']    = pageSize
pagingShader['numPages']    = numPages
pagingShader['pagesAcross'] = pagesAcross
pagingShader['worldSize']   = 60000
data = np.zeros(4,dtype=[("position" , np.float32,3)])
data['position'] = [(-1,-1,0.999999),(-1,1,0.999999),(1,-1,0.999999),(1,1,0.999999)]
I = [0,1,2, 1,2,3]
indices = np.array(I,dtype=np.int32)
pagingRenderID = pagingShader.setData(data,indices)

def getCoordinate(id):
  """Given a page id, returns the page coordinates in the page table."""
  return id % numPages, id / numPages

def generatePage(page):
  assert page in pageMapping
  c = getCoordinate(pageMapping[page])
  logging.info("Generating global page {} (in page {})".format(page, c))
  pageRenderStage.load(pageResoultion,pageResoultion, pageResoultion*c[0],pageResoultion*(numPages-c[1]-1),False)
  pagingShader.load()
  pagingShader['pagePosition'] = np.array([page[0],0.,page[1]],dtype=np.float32)
  pagingShader['id'] = pageMapping[page]
  pagingShader.draw(gl.GL_TRIANGLES, pagingRenderID)

def updatePageTable(camera):
  if camera.position[1] > 5000:
    if len(pageMapping):
      logging.info("Clearing all pages due to high camera.")
      pageMapping.clear()
    return

  currentPage = (pagesAcross - int(camera.position[2] / (pageSize) + pagesAcross/2),
                               int(camera.position[0] / (pageSize) + pagesAcross/2))
  toredo = False
  for i in xrange(max(0,currentPage[0]-numPages/2),min(pagesAcross,currentPage[0]+numPages/2+1)):
    for j in xrange(max(0,currentPage[1]-numPages/2),min(pagesAcross,currentPage[1]+numPages/2+1)):
      if (i,j) not in pageMapping:
        logging.info("Page {} not present.".format((i,j)))
        toredo = True
        break
  if not toredo: return

  data = np.zeros((pagesAcross, pagesAcross, 4),dtype=np.float32) - 1
  for i in xrange(max(0,currentPage[0]-numPages/2),min(pagesAcross,currentPage[0]+numPages/2+1)):
    for j in xrange(max(0,currentPage[1]-numPages/2),min(pagesAcross,currentPage[1]+numPages/2+1)):
      page = (i,j)
      if page not in pageMapping:
        pageMapping.add(page)
        generatePage(page)
      index = pageMapping[page]
      data[i][j][0] = index / float(numPages**2)
  pageTableTexture.loadData(data[::-1,:])
