#!/usr/bin/env python
"""Script that generates a novel (!)"""

from pattern.en import numerals, pluralize, referenced, singularize

import json
import logging, logging.handlers
import random
import re
import sys

class Journey:
   """Class that does all the heavy lifting"""

   CHAPTER = 0

   TEXT = ''
   TEMP = ''

   MAZE = []
   MAZE_SIZE = 25
   MAZE_EXIT = {}

   DIR_INDEX   = 0
   DIR_STRINGS = {'n': ['north', 'up'], 's': ['south', 'down'], 'e': ['east', 'right'], 'w': ['west', 'left']}
   OPPOSITE    = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}

   FOUND_EXIT = False

   JSON = {}

   WALK = ['walked', 'went', 'strode', 'ran', 'sprinted', 'hoofed it', 'beat cheeks', 'trekked', 'meandered', 'marched', 'shuffled', 'shambled', 'toddled', 'traipsed', 'plodded', 'strutted', 'trudged', 'paraded', 'hiked', 'ambled', 'sauntered', 'stepped']

   # -------------------------------------------------------------------------------------------------------------
   def __init__(self):
      """Constructor"""

      self.load_json()

   # -------------------------------------------------------------------------------------------------------------
   def load_json(self):
      """Pulls various corpora and loads them into the JSON object"""

      f = open('corpora/data/flowers/flowers.json')
      self.JSON['flowers'] = json.loads(f.read().lower())['flowers']
      f.close()

      f = open('corpora/data/animals/common.json')
      self.JSON['animals'] = json.loads(f.read().lower())['animals']
      f.close()

      f = open('corpora/data/colors/crayola.json')
      self.JSON['colors'] = json.loads(f.read().lower())['colors']
      f.close()

      f = open('corpora/data/foods/fruits.json')
      self.JSON['fruits'] = json.loads(f.read().lower())['fruits']
      f.close()

      f = open('corpora/data/humans/firstNames.json')
      self.JSON['names'] = json.loads(f.read())['firstNames']
      f.close()

   # -------------------------------------------------------------------------------------------------------------
   def init_maze(self):
      """Initializes the maze object"""

      self.MAZE = []
      self.TEMP = ''

      self.DIR_INDEX = random.randrange(2)

      for i in range(0, self.MAZE_SIZE):
         self.MAZE.append([])

         for j in range(0, self.MAZE_SIZE):
            self.MAZE[i].append({'n': 0, 's': 0, 'e': 0, 'w': 0, 'v': 0})

   # -------------------------------------------------------------------------------------------------------------
   def reset_maze(self):
      """Resets the visited flag on each square to 0"""

      for i in range(0, self.MAZE_SIZE):
         for j in range(0, self.MAZE_SIZE):
            self.MAZE[i][j]['v'] = 0

   # -------------------------------------------------------------------------------------------------------------
   def next_maze(self, i, j):
      """Returns a list which is the "next" square in a maze traversal and the direction it came from"""

      next = None

      # Keeps track of valid directions to go from 'here' (unvisited squares)
      dirs = []

      try:
         if not self.MAZE[i][j - 1]['v']:
            dirs.append('n')
      except IndexError:
         pass

      try:
         if not self.MAZE[i][j + 1]['v']:
            dirs.append('s')
      except IndexError:
         pass

      try:
         if not self.MAZE[i + 1][j]['v']:
            dirs.append('e')
      except IndexError:
         pass

      try:
         if not self.MAZE[i - 1][j]['v']:
            dirs.append('w')
      except IndexError:
         pass

      if len(dirs):
         # Pick a random direction and update the current square's visited flag and the wall flag in that direction
         dir = random.choice(dirs)
         self.MAZE[i][j][dir] = 1

         # Find the next square in the random direction and update those flags, too
         if dir == 'n':
            j -= 1

         if dir == 's':
            j += 1

         if dir == 'e':
            i += 1

         if dir == 'w':
            i -= 1

         next = [i, j, self.OPPOSITE[dir]]

      return next       

   # -------------------------------------------------------------------------------------------------------------
   def build_maze(self):
      """Builds a new random maze"""

      stack = []

      self.init_maze()

      # Pick an exit at random
      i = random.randint(5, self.MAZE_SIZE - 5)
      j = random.randint(5, self.MAZE_SIZE - 5)
      stack.append({'i': i, 'j': j})
      self.MAZE_EXIT = stack[0]
      square = stack[0]
      logging.info('Maze exit at (' + str(i) + ',' + str(j) + ')')

      total = 0
      # Run through the maze checking visiting every square 
      while (len(stack)):

         i = square['i']
         j = square['j']

         # Get a random neighbor that hasn't been visited
         next = self.next_maze(i, j)

         # If one was found, add it to the stack and flip its visited flag
         if next:

            i = next[0]
            j = next[1]

            self.MAZE[i][j]['v'] = 1
            self.MAZE[i][j][next[2]] = 1

            stack.append({'i': i, 'j': j})
            total += 1

         # Or if there are no valid directions, step back through the path to get to a square with
         # unvisited neighbors
         else:
            square = stack.pop()

 
      # Reset the visited flags on each square
      self.reset_maze()

      logging.info('Built Maze... (' + str(total) + ')')

   # -------------------------------------------------------------------------------------------------------------
   def traverse_maze(self):
      """Traverses the maze from a random start point"""

      stack = []
      self.TEMP = ''

      # Pick a start point at random
      i = random.randrange(self.MAZE_SIZE)
      j = random.randrange(self.MAZE_SIZE)
      stack.append({'i': i, 'j': j})
      square = stack[0]
      logging.info('Starting maze at (' + str(i) + ',' + str(j) + ')')

      then = False

      total = 0
      last_dir = ''
      # Run through the maze 
      while (len(stack)):

         i = square['i']
         j = square['j']

         # Get a random neighbor that hasn't been visited
         next = self.next_maze(i, j)

         # If one was found, add it to the stack and flip its visited flag
         if next:

            i = next[0]
            j = next[1]

            # If we found an exit!
            if self.MAZE_EXIT['i'] == i and self.MAZE_EXIT['j'] == j:
               self.CHAPTER += 1
               
               self.TEXT += "~~~ CHAPTER " + numerals(str(self.CHAPTER)).upper() + " ~~~\n"
               self.TEXT += self.TEMP
               self.TEXT += "Then I " + random.choice(self.WALK) + " down a flight of stairs.\n"

               self.FOUND_EXIT = True

               logging.info('Found the exit to the maze at (' + str(i) + ',' + str(j) + ')')
               logging.info('Total steps: ' + str(total))
               stack = []

            else:
               if last_dir == self.OPPOSITE[next[2]] and then:
                  self.TEMP += "Again I " + random.choice(self.WALK) + " " + self.DIR_STRINGS[self.OPPOSITE[next[2]]][self.DIR_INDEX] + ". "
               elif then:
                  self.TEMP += "Then I " + random.choice(self.WALK) + " " + self.DIR_STRINGS[self.OPPOSITE[next[2]]][self.DIR_INDEX] + ". "
               else:
                  self.TEMP += "I " + random.choice(self.WALK) + " " + self.DIR_STRINGS[self.OPPOSITE[next[2]]][self.DIR_INDEX] + ". "
                  then = True

               # Is there a flower here?
               if random.randrange(100) < 5:
                  self.TEMP += "There was a beautiful " + random.choice(self.JSON['colors'])['color'] + " "
                  self.TEMP += singularize(random.choice(self.JSON['flowers'])) + " there. "
                  self.TEMP += "It smelled like " + pluralize(random.choice(self.JSON['fruits'])) + ".\n"
               # Or is there an animal here?
               elif random.randrange(100) < 5:
                  self.TEMP += "There was " + referenced(random.choice(self.JSON['animals'])) + " there. "
                  self.TEMP += "I named it " + random.choice(self.JSON['names']) + ".\n"

               self.MAZE[i][j]['v'] = 1
               self.MAZE[i][j][next[2]] = 1

               stack.append({'i': i, 'j': j})
               total += 1

               last_dir = self.OPPOSITE[next[2]]

         # Or if there are no valid directions, step back through the path to get to a square with
         # unvisited neighbors
         else:
            if random.randrange(100) < 5:
               self.TEMP += "Then I hit a dead-end. I was feeling lost so I retraced my steps.\n"
               then = False

            square = stack.pop()

   # -------------------------------------------------------------------------------------------------------------
   def count_words(self):
      """Returns the current number of words in the text"""

      return len(re.split(r'[^0-9A-Za-z]+', self.TEXT))

   # -------------------------------------------------------------------------------------------------------------
   def write_text(self):
      """Writes the TEXT attribute out to a file"""

      text = ""

      for line in self.TEXT.split("\n"):
         
         if len(line) > 80:

            count = 0
            space = 0
            start = 0
            for i in range(len(line)):
               c = line[i]

               if c == ' ': 
                  space = i

               if count >= 80:
                  text += line[start:space].strip() + "\n"
                  start = space
                  i = space
                  count = 0

               else:
                  count += 1

            text += line[start:].strip() + "\n\n"

         else:
            text += line + "\n\n"

      text  = "~~~ FORWARD ~~~\n\nI am an adventurer. I came to this complex of mazes to seek glory.\nWhat follows is the journal of my travails.\n\n" + text.strip()
      text += "\n\n~~~ AFTERWARD ~~~\n\nI sought glory, and I found it at the bottom of this massive place.\n\nTHE END\n"

      f = open('journey.txt', 'w')
      f.write(text)
      f.close()

# -------------------------------------------------------------------------------------------------------------
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

   while j.count_words() < 50000:
      j.build_maze()
      j.traverse_maze()

   j.write_text()

   logging.info('Done, with ' + str(j.count_words()) + ' words')

# -------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   sys.exit(main())
