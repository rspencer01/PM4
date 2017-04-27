import Object

characters = [
Object.Object(
  'assets/knight/models/knight.fbx',
  'Knight',
  scale=0.1,
  position=(-183, 0,-2938),
  offset=(-758, -479, -728))]


def display():
  for i in characters:
    i.display()
