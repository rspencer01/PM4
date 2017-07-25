import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--remake-noise', action='store_true')
parser.add_argument('--remake-trees', action='store_true')
parser.add_argument('--remake-sky', action='store_true')
parser.add_argument('--remake-stars', action='store_true')
parser.add_argument('--remake-terrain', action='store_true')
parser.add_argument('--disable-atmosphere', action='store_true')
parser.add_argument('--remake-config-file', action='store_true')
parser.add_argument('--remake-roads', action='store_true')
parser.add_argument('--monolith', action='store_true')
parser.add_argument('--reload-textures', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')

parser.add_argument('--replay', default=None)

def parse():
  global args
  args = parser.parse_args()
