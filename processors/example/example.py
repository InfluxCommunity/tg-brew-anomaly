# A simple processor. It reads stdin and writes it to stdout.
import sys

def main():
   for line in sys.stdin:
       print(line.rstrip())
       sys.stdout.flush()

if __name__ == '__main__':
   main()