#!/usr/bin/env python
"""Script that generates a novel (!)"""

import logging, logging.handlers
import random
import sys


class Journey:
   """Class that does all the heavy lifting"""

   MAZE = []
   MAZE_SIZE = 25

   def build_maze(self):
      """Builds a new random maze"""

      stack = []
      self.MAZE = []

      # Initialize maze to empty lists with unvisited squres
      for i in range(0, self.MAZE_SIZE):
         self.MAZE.append([])

         for j in range(0, self.MAZE_SIZE):
            self.MAZE[i].append({'n': 0, 's': 0, 'e': 0, 'w': 0, 'v': 0})

      # Pick an exit at random
      i = random.randint(2, self.MAZE_SIZE - 2)
      j = random.randint(2, self.MAZE_SIZE - 2)
      stack.append({'i': i, 'j': j})
      square = stack[0]
      logging.info('Maze exit at (' + str(i) + ',' + str(j) + ')')

      total = 0
      # Build out the rest of the maze
      while (len(stack)):

         i = square['i']
         j = square['j']

         # Keeps track of valid directions to go from 'here' (unvisited squares)
         dirs = []

         try:
            if (not self.MAZE[i][j - 1]['v']):
               dirs.append('n')
         except IndexError:
            pass

         try:
            if (not self.MAZE[i][j + 1]['v']):
               dirs.append('s')
         except IndexError:
            pass

         try:
            if (not self.MAZE[i + 1][j]['v']):
               dirs.append('e')
         except IndexError:
            pass

         try:
            if (not self.MAZE[i - 1][j]['v']):
               dirs.append('w')
         except IndexError:
            pass

         if (len(dirs)):
            # Pick a random direction and update the current square's visited flag and the wall flag in that direction
            dir = random.choice(dirs)
            self.MAZE[i][j][dir] = 1

            # Find the next square in the random direction and update those flags, too
            if (dir == 'n'):
               w = 's'
               j -= 1

            if (dir == 's'):
               w = 'n'
               j += 1

            if (dir == 'e'):
               w = 'w'
               i += 1

            if (dir == 'w'):
               w = 'e'
               i -= 1

            self.MAZE[i][j]['v'] = 1
            self.MAZE[i][j][w] = 1

            stack.append({'i': i, 'j': j})
            total += 1

         else:
            # Or if there are no valid directions, step back through the path to get to a square with
            # unvisited neighbors
            square = stack.pop()


      logging.info('Built Maze...')


def main():
   """Main entry point"""

   # Set up logging
   logging.getLogger().level = logging.INFO
   format = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)-5.5s]  %(message)s')

   streamHandler = logging.StreamHandler()
   streamHandler.setFormatter(format)
   logging.getLogger().addHandler(streamHandler)

   fileHandler = logging.handlers.RotatingFileHandler('journey.log', 'a', 1024 * 1024, 3, 'utf-8')
   fileHandler.setFormatter(format)
   logging.getLogger().addHandler(fileHandler)

   # Instantiate main object and begin
   j = Journey()
   j.build_maze()


if __name__ == '__main__':
   sys.exit(main())
