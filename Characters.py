import Object

characters = [
Object.Object(
  'assets/knight/models/knight.fbx',
  'Knight',
  scale=0.03,
  position=(-183, 0,-2938),
  offset=(-758, -477.7, -728))]


def display():
  for i in characters:
    i.display()
