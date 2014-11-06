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

   TITLE = "FLORA AND FAUNA"

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

   TASTES = ['awful', 'delicious', 'terrible', 'like chicken', 'okay', 'bad', 'good']

   FLOWERS = []
   TEMP_FLOWERS = []

   ANIMALS = []
   TEMP_ANIMALS = []

   # -------------------------------------------------------------------------------------------------------------
   def __init__(self):
      """Constructor"""

      self.load_json()

   # -------------------------------------------------------------------------------------------------------------
   def load_json(self):
      """Pulls various corpora and loads them into the JSON object"""

      f = open('corpora/data/plants/flowers.json')
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
      self.TEMP_FLOWERS = []
      self.TEMP_ANIMALS = []

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
      self.TEMP_FLOWERS = []
      self.TEMP_ANIMALS = []

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
               self.TEXT += "Then I " + random.choice(self.WALK) + " down a flight of stairs. "

               self.FLOWERS += self.TEMP_FLOWERS
               self.ANIMALS += self.TEMP_ANIMALS

               # Check to see if any animals stopped following the narrator
               self.TEXT += self.unfollow()

               if self.ANIMALS:
                  self.TEXT += "So far " + numerals(len(self.ANIMALS)) + " animal"

                  if len(self.ANIMALS) > 1:
                     self.TEXT += "s were following me"
                  else:
                     self.TEXT += " was following me"

                  if self.FLOWERS:
                     self.TEXT += ", and "

                  else:
                     self.TEXT += ". "

               if self.FLOWERS:
                  if not self.ANIMALS:
                     self.TEXT += "So far "

                  self.TEXT += "I held " + numerals(len(self.FLOWERS)) + " flower"

                  if len(self.FLOWERS) > 1:
                     self.TEXT += "s"

                  self.TEXT += ". "

               self.TEXT += "\n"

               self.FOUND_EXIT = True

               logging.info('--- CHAPTER ' + str(self.CHAPTER) + ' ---')
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
                  color  = random.choice(self.JSON['colors'])['color']
                  flower = singularize(random.choice(self.JSON['flowers']))

                  self.TEMP += "There was a beautiful " + color + " " + flower + " there. "
                  self.TEMP += "It smelled like " + pluralize(random.choice(self.JSON['fruits'])) + "."

                  # Is the narrator keeping this flower?
                  if random.randrange(100) < 10:
                     self.TEMP += " I picked it"

                     if self.TEMP_FLOWERS:
                        self.TEMP += " and added it to the rest of my bouquet"
                     self.TEMP += "."

                     self.TEMP_FLOWERS.append(referenced(color + " " + flower))

                  # Does the narrator eat this flower instead?
                  elif random.randrange(100) < 5:
                     self.TEMP += " For some reason I ate it. It tasted " + random.choice(self.TASTES) + "."

                  self.TEMP += "\n"
                  then = False

               # Or is there an animal here?
               elif random.randrange(100) < 5:
                  animal = random.choice(self.JSON['animals'])
                  name = random.choice(self.JSON['names'])

                  self.TEMP += "There was " + referenced(animal) + " there. "
                  self.TEMP += "I named it " + name + "."

                  # Did the animal follow the narrator?
                  if random.randrange(100) < 10:
                     self.TEMP_ANIMALS.append(name + " the " + animal)
                     self.TEMP += " It started following me."

                  self.TEMP += "\n"

                  then = False

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
   def unfollow(self):
      """Loop through the following animals list and randomly pick some to remove"""

      unfollowed = []
      for a in self.ANIMALS:
         if random.randrange(100) < 3:
            unfollowed.append(a)
            self.ANIMALS.remove(a)

      temp = ""
      for a in unfollowed:
         if a == unfollowed[-1] and len(unfollowed) > 1:
            temp += ", and "
         elif a != unfollowed[0]:
            temp += ", "

         temp += a

      if temp:
         temp += " stopped following me for some reason.\n"

      return temp

   # -------------------------------------------------------------------------------------------------------------
   def count_words(self):
      """Returns the current number of words in the text"""

      return len(re.split(r'[^0-9A-Za-z]+', self.full_text()))

   # -------------------------------------------------------------------------------------------------------------
   def get_prologue(self):
      """Returns the assembled prologue"""

      temp  = "~~~ PROLOGUE ~~~\nI am a botanist and a zoologist. "
      temp += "I came to this complex of mazes to catalog flora and fauna. "
      temp += "What follows is the journal of my travails.\n"

      return temp

   # -------------------------------------------------------------------------------------------------------------
   def get_afterword(self):
      """Returns the assembled afterword"""

      temp  = "\n~~~ AFTERWORD ~~~\n"
      temp += "I finally made my way through every floor and out into the sunlight. "
      temp += "Below is a list of some of the things I cataloged inside this massive place.\n"
      temp += self.get_animals()
      temp += self.get_flowers()
      temp += "\nTHE END\n"

      return temp

   # -------------------------------------------------------------------------------------------------------------
   def get_animals(self):
      """Returns a textual representation of following animals"""

      temp = ""
      if self.ANIMALS:
         temp += "I was followed by: "

         for a in self.ANIMALS:
            if a == self.ANIMALS[-1] and len(self.ANIMALS) > 1:
               temp += ", and "

            elif a != self.ANIMALS[0]: 
               temp += ", "

            temp += a

      return temp + ".\n"

   # -------------------------------------------------------------------------------------------------------------
   def get_flowers(self):
      """Returns a textual representation of carried flowers"""

      temp = ""
      if self.FLOWERS:
         temp += "I left with a beautiful bouquet of flowers that contained: "

         for f in self.FLOWERS:
            if f == self.FLOWERS[-1] and len(self.FLOWERS) > 1:
               temp += ", and "

            elif f != self.FLOWERS[0]:
               temp += ", "

            temp += f

      return temp + ".\n"

   # -------------------------------------------------------------------------------------------------------------
   def full_text(self):
      """Returns the full text of the novel as a string"""

      return self.TITLE + "\n" + self.get_prologue() + self.TEXT + self.get_afterword()

   # -------------------------------------------------------------------------------------------------------------
   def write_text(self):
      """Writes the TEXT attribute out to a file"""

      text = ""

      for line in self.full_text().split("\n"):
         
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
