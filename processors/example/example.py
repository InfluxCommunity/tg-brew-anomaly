# The simplest possible processor. It reads stdin and writes it to stdout.
import sys

for line in sys.stdin:
  print(line.rstrip())
  sys.stdout.flush()