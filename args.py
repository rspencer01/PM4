import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--remake-noise', action='store_true')
parser.add_argument('--remake-trees', action='store_true')
parser.add_argument('--remake-sky', action='store_true')
parser.add_argument('--remake-terrain', action='store_true')

def parse():
  global args
  args = parser.parse_args()