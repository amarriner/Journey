#!/usr/bin/env python
"""Script that generates a novel (!)"""

from pattern.en import numerals, pluralize, referenced, singularize

import gd
import json
import logging, logging.handlers
import os
import random
import re
import requests
import sys

CONCEPTNET_URL = "http://conceptnet5.media.mit.edu/data/5.2/c/en/"

class Journey:
   """Class that does all the heavy lifting"""

   # Title of the book
   TITLE = "FLORA AND FAUNA"

   # Keeping track of chapter numbers
   CHAPTER = 0

   TEXT = ''
   TEMP = ''
   THEN = False
   DEBUG = ''

   # Maze variables
   MAZE = []
   MAZE_SIZE = 25
   MAZE_EXIT = {}
   MAZE_START = {}
   FOUND_EXIT = False
   DIR_INDEX   = 0
   DIR_STRINGS = {'n': ['north', 'up'], 's': ['south', 'down'], 'e': ['east', 'right'], 'w': ['west', 'left']}
   OPPOSITE    = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}

   JSON = {}
   COLORS = {}

   # Variations of "walk"
   WALK = ['walked', 'went', 'strode', 'ran', 'sprinted', 'hoofed it', 'beat cheeks', 'trekked', 'meandered', 'marched', 'shuffled', 'shambled', 'toddled', 'traipsed', 'plodded', 'strutted', 'trudged', 'paraded', 'hiked', 'ambled', 'sauntered', 'stepped']

   # Options for flower tastes
   TASTES = ['awful', 'delicious', 'terrible', 'like chicken', 'okay', 'bad', 'good']

   # List of flowers held by the narrator
   FLOWERS = []
   TEMP_FLOWERS = []

   # Lists of animals and their conversations
   ANIMALS = []
   CONVOS = {}
   TEMP_ANIMALS = []
   TEMP_CONVOS = {}
   ANIMAL_CONCEPTS = {}

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

      if os.path.exists('concepts.json'):
         f = open('concepts.json')
         self.ANIMAL_CONCEPTS = json.loads(f.read())
         f.close()

   # -------------------------------------------------------------------------------------------------------------
   def init_maze(self):
      """Initializes the maze object"""

      self.MAZE = []
      self.TEMP = ''
      self.DEBUG = ''
      self.TEMP_FLOWERS = []
      self.TEMP_ANIMALS = []

      self.DIR_INDEX = random.randrange(2)

      for i in range(0, self.MAZE_SIZE):
         self.MAZE.append([])

         for j in range(0, self.MAZE_SIZE):
            self.MAZE[i].append({'n': 0, 's': 0, 'e': 0, 'w': 0, 'v': 0})

            self.IMAGE.rectangle((i * 15, j * 15), (i * 15 + 14, j * 15 + 14), self.COLORS['blue'])
            self.IMAGE.rectangle((i * 15 + 1, j * 15 + 1), (i * 15 + 13, j * 15 + 13), self.COLORS['blue'])

   # -------------------------------------------------------------------------------------------------------------
   def reset_maze(self):
      """Resets the visited flag on each square to 0"""

      for i in range(0, self.MAZE_SIZE):
         for j in range(0, self.MAZE_SIZE):
            self.MAZE[i][j]['v'] = 0

   # -------------------------------------------------------------------------------------------------------------
   def next_maze(self, i, j, build = False):
      """Returns a list which is the "next" square in a maze traversal and the direction it came from"""

      start = None
      next = None

      # Keeps track of valid directions to go from 'here' (unvisited squares)
      dirs = []

      # If we're building the maze, not traversing it, only check the visited flag in a given square
      if build:
         if j - 1 >= 0:
            if not self.MAZE[i][j - 1]['v']:
               dirs.append('n')

         if j + 1 < self.MAZE_SIZE:
            if not self.MAZE[i][j + 1]['v']:
               dirs.append('s')

         if i + 1 < self.MAZE_SIZE:
            if not self.MAZE[i + 1][j]['v']:
               dirs.append('e')

         if i - 1 >= 0:
            if not self.MAZE[i - 1][j]['v']:
               dirs.append('w')

      # If we're traversing the maze, not building it check the existence of a wall in the given direction 
      # as well as the visited flag
      else:
         if j - 1 >= 0:
#            if self.MAZE_START['i'] == i and self.MAZE_START['j'] == j - 1:
#               start = 'n'

            if self.MAZE[i][j - 1]['s'] and not self.MAZE[i][j - 1]['v']:
               dirs.append('n')

         if j + 1 < self.MAZE_SIZE:
#            if self.MAZE_START['i'] == i and self.MAZE_START['j'] == j + 1:
#               start = 's'

            if self.MAZE[i][j + 1]['n'] and not self.MAZE[i][j + 1]['v']:
               dirs.append('s')

         if i + 1 < self.MAZE_SIZE:
#            if self.MAZE_START['i'] == i + 1 and self.MAZE_START['j'] == j:
#               start = 'e'

            if self.MAZE[i + 1][j]['w'] and not self.MAZE[i + 1][j]['v']:
               dirs.append('e')

         if i - 1 >= 0:
#            if self.MAZE_START['i'] == i - 1 and self.MAZE_START['j'] == j:
#               start = 'w'

            if self.MAZE[i - 1][j]['e'] and not self.MAZE[i - 1][j]['v']:
               dirs.append('w')

#      if start and not len(dirs):
#         dirs.append(start)

      if len(dirs):
         # Pick a random direction and update the current square's visited flag and the wall flag in that direction
         dir = random.choice(dirs)
         self.MAZE[i][j][dir] = 1

         # Find the next square in the random direction and update those flags, too
         # and remove the walls on the map image
         if dir == 'n':
            if build:
               self.IMAGE.rectangle((i * 15 + 2, j * 15), (i * 15 + 12, j * 15 + 1), self.COLORS['white'])

            j -= 1

            if build:
               self.IMAGE.rectangle((i * 15 + 2, j * 15 + 13), (i * 15 + 12, j * 15 + 14), self.COLORS['white'])

         if dir == 's':
            if build:
               self.IMAGE.rectangle((i * 15 + 2, j * 15 + 13), (i * 15 + 12, j * 15 + 14), self.COLORS['white'])

            j += 1

            if build:
               self.IMAGE.rectangle((i * 15 + 2, j * 15), (i * 15 + 12, j * 15 + 1), self.COLORS['white'])

         if dir == 'e':
            if build:
               self.IMAGE.rectangle((i * 15 + 13, j * 15 + 2), (i * 15 + 14, j * 15 + 12), self.COLORS['white'])

            i += 1

            if build:
               self.IMAGE.rectangle((i * 15, j * 15 + 2), (i * 15 + 1, j * 15 + 12), self.COLORS['white'])

         if dir == 'w':
            if build:
               self.IMAGE.rectangle((i * 15, j * 15 + 2), (i * 15 + 1, j * 15 + 12), self.COLORS['white'])

            i -= 1

            if build:
               self.IMAGE.rectangle((i * 15 + 13, j * 15 + 2), (i * 15 + 14, j * 15 + 12), self.COLORS['white'])

         next = [i, j, self.OPPOSITE[dir]]

      if not build:
         if len(dirs):
            self.DEBUG += "Available directions from (" + str(i) + "," + str(j) + "): " + str.join(" : ", dirs) + "\n"
         else:
            self.DEBUG += "No valid directions from (" + str(i) + "," + str(j) + ")!\n"

      return next       

   # -------------------------------------------------------------------------------------------------------------
   def build_maze(self):
      """Builds a new random maze"""

      stack = []

      self.IMAGE = gd.image((self.MAZE_SIZE * 15, self. MAZE_SIZE * 15))
      self.COLORS['black']  = self.IMAGE.colorAllocate((0, 0, 0))
      self.COLORS['white']  = self.IMAGE.colorAllocate((255, 255, 255))
      self.COLORS['blue']   = self.IMAGE.colorAllocate((130, 130, 210))
      self.COLORS['red']    = self.IMAGE.colorAllocate((210, 130, 130))
      self.COLORS['orange'] = self.IMAGE.colorAllocate((255, 165, 0))
      self.COLORS['green']  = self.IMAGE.colorAllocate((130, 210, 130))
      self.COLORS['yellow'] = self.IMAGE.colorAllocate((255, 255, 200))
      self.COLORS['purple'] = self.IMAGE.colorAllocate((210, 130, 210))
      self.COLORS['grey']   = self.IMAGE.colorAllocate((180, 180, 180))
      self.IMAGE.filledRectangle((0, 0), (self.MAZE_SIZE * 15, self. MAZE_SIZE * 15), self.COLORS['white'])

      self.init_maze()

      # Pick an exit at random
      i = random.randint(5, self.MAZE_SIZE - 5)
      j = random.randint(5, self.MAZE_SIZE - 5)
      self.IMAGE.filledRectangle((i * 15 + 4, j * 15 + 4), (i * 15 + 11, j * 15 + 11), self.COLORS['orange'])
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
         next = self.next_maze(i, j, True)

         # If one was found, add it to the stack and flip its visited flag
         if next:

            self.MAZE[i][j]['v'] = 1
            self.MAZE[i][j][self.OPPOSITE[next[2]]] = 1
            stack.append({'i': i, 'j': j})

            i = next[0]
            j = next[1]

            self.MAZE[i][j]['v'] = 1
            self.MAZE[i][j][next[2]] = 1

            square = {'i': i, 'j': j}
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
      self.TEMP_CONVOS = self.CONVOS

      # Pick a start point at random
      i = random.randrange(self.MAZE_SIZE)
      j = random.randrange(self.MAZE_SIZE)
      stack.append({'i': i, 'j': j})
      square = stack[0]
      logging.info('Starting maze at (' + str(i) + ',' + str(j) + ')')
      self.IMAGE.filledRectangle((i * 15 + 4, j * 15 + 4), (i * 15 + 11, j * 15 + 11), self.COLORS['grey'])
      self.MAZE_START = square

      self.THEN = False

      total = 0
      last_dir = ''
      last_i = -1
      last_j = -1
      # Run through the maze 
      while (len(stack)):

         i = square['i']
         j = square['j']

         self.DEBUG += "Square = (" + str(i) + "," + str(j) + ")\n"

         # Get a random neighbor that hasn't been visited
         next = self.next_maze(i, j)

         # If one was found, add it to the stack and flip its visited flag
         if next:
            if square not in stack:
               stack.append(square)

            first_dead_end = True

            last_i = i
            last_j = j

            self.DEBUG += "Moving " + self.OPPOSITE[next[2]] + "\n"

            i = next[0]
            j = next[1]

            self.MAZE[i][j]['v'] = 1
            square = {'i': i, 'j': j}

            # If we found an exit!
            if self.MAZE_EXIT['i'] == i and self.MAZE_EXIT['j'] == j:

               self.do_exit(i, j, total, next, last_i, last_j)

               stack = []

            # Otherwise keep walking
            else:

               if last_dir == self.OPPOSITE[next[2]] and self.THEN:
                  self.TEMP += "Again I " + random.choice(self.WALK) + " " + self.DIR_STRINGS[self.OPPOSITE[next[2]]][self.DIR_INDEX] + ". "
               elif self.THEN:
                  self.TEMP += "Then I " + random.choice(self.WALK) + " " + self.DIR_STRINGS[self.OPPOSITE[next[2]]][self.DIR_INDEX] + ". "
               else:
                  self.TEMP += "I " + random.choice(self.WALK) + " " + self.DIR_STRINGS[self.OPPOSITE[next[2]]][self.DIR_INDEX] + ". "
                  self.THEN = True

               # Is there a flower here?
               if random.randrange(100) < 5:

                  self.do_flower(i, j)

               # Or is there an animal here?
               elif random.randrange(100) < 5:

                  self.do_animal(i, j)

               # Or are two animals talking to each other?
               elif random.randrange(100) < 1 and len(self.ANIMALS) + len(self.TEMP_ANIMALS) > 1:

                  self.do_animal_conversation(i, j)

               self.MAZE[i][j]['v'] = 1
               self.MAZE[i][j][next[2]] = 1

               stack.append({'i': i, 'j': j})
               total += 1

               last_dir = self.OPPOSITE[next[2]]

            if next[2] in ['e', 'w']:
               self.IMAGE.filledRectangle((last_i * 15 + 7, last_j * 15 + 6), (i * 15 + 7, j * 15 + 8), self.COLORS['green'])
            else:
               self.IMAGE.filledRectangle((last_i * 15 + 6, last_j * 15 + 7), (i * 15 + 8, j * 15 + 7), self.COLORS['green'])

         # Or if there are no valid directions, step back through the path to get to a square with
         # unvisited neighbors
         else:
            if first_dead_end:
               self.TEMP += "Then I hit a dead-end. I was feeling lost so I retraced my steps.\n"
               self.THEN = False
               first_dead_end = False

            self.DEBUG += "Couldn't find a neighbor, popping stack\n"
            square = stack.pop()

   # -------------------------------------------------------------------------------------------------------------
   def do_exit(self, i, j, total, next, last_i, last_j):
      """Process the end of a floor"""

      self.FOUND_EXIT = True

      # Place the last path on the image
      if next[2] in ['e', 'w']:
         self.IMAGE.filledRectangle((last_i * 15 + 7, last_j * 15 + 6), (i * 15 + 7, j * 15 + 8), self.COLORS['green'])
      else:
         self.IMAGE.filledRectangle((last_i * 15 + 6, last_j * 15 + 7), (i * 15 + 8, j * 15 + 7), self.COLORS['green'])

      # Increment chapter, and write it
      self.CHAPTER += 1
      self.TEXT += "~~~ CHAPTER " + numerals(str(self.CHAPTER)).upper() + " ~~~\n"
      self.TEXT += self.TEMP
      self.TEXT += "Then I " + random.choice(self.WALK) + " down a flight of stairs. "

      # Write the current map out to PNG
      self.IMAGE.writePng("html/maps/" + str(self.CHAPTER) + ".png")

      # Store flowers held, animals following, and conversations permanently
      self.FLOWERS += self.TEMP_FLOWERS
      self.ANIMALS += self.TEMP_ANIMALS
      for c in self.TEMP_CONVOS:
         if c not in self.CONVOS.keys():
            self.CONVOS[c] = []

         self.CONVOS[c].append(self.TEMP_CONVOS[c])

      # Check to see if any animals stopped following the narrator, then print them
      self.TEXT += self.unfollow()
      self.get_animals_following()
      self.get_flowers_held()

      # Logging...
      logging.info('--- CHAPTER ' + str(self.CHAPTER) + ' ---')
      logging.info('Found the exit to the maze at (' + str(i) + ',' + str(j) + ')')
      logging.info('Total steps: ' + str(total))

   # -------------------------------------------------------------------------------------------------------------
   def do_flower(self, i, j):
      """Process finding a flower and possibly doing something with it"""

      # Get a random color and flower name
      color  = random.choice(self.JSON['colors'])['color']
      flower = singularize(random.choice(self.JSON['flowers']))

      # Print them
      self.TEMP += "There was a beautiful " + color + " " + flower + " there. "
      self.TEMP += "It smelled like " + pluralize(random.choice(self.JSON['fruits'])) + "."

      # Put a square on the map to mark the flower
      self.IMAGE.filledRectangle((i * 15 + 4, j * 15 + 4), (i * 15 + 11, j * 15 + 10), self.COLORS['purple'])

      # Is the narrator keeping this flower?
      if random.randrange(100) < 10:
         self.TEMP += " I picked it"

         if self.TEMP_FLOWERS:
            self.TEMP += " and added it to the rest of my bouquet"
 
         self.TEMP += "."

         self.TEMP_FLOWERS.append({'color': color, 'flower': flower})

      # Does the narrator eat this flower instead?
      elif random.randrange(100) < 5:
         self.TEMP += " For some reason I ate it. It tasted " + random.choice(self.TASTES) + "."

      self.TEMP += "\n"
      self.THEN = False

   # -------------------------------------------------------------------------------------------------------------
   def do_animal(self, i, j):
      """Process finding an animal"""

      # Get a random animal and give it a name
      animal = random.choice(self.JSON['animals'])
      name = random.choice(self.JSON['names'])

      # Print that info
      self.TEMP += "There was " + referenced(animal) + " there. "
      self.TEMP += "I named it " + name + "."

      # Put a square on the map to denote finding an animal here
      self.IMAGE.filledRectangle((i * 15 + 4, j * 15 + 4), (i * 15 + 11, j * 15 + 10), self.COLORS['red'])

      # Did the animal follow the narrator?
      if random.randrange(100) < 10:
         self.TEMP_ANIMALS.append({'name': name, 'animal': animal})
         self.get_animal_concepts(animal)
         self.TEMP += " It started following me."
         self.TEMP += "\n"

      self.THEN = False

   # -------------------------------------------------------------------------------------------------------------
   def do_animal_conversation(self, i, j):
      """Make two animals talk to one another"""

      # Make sure we have the entire list of animals and conversations
      all_animals = self.ANIMALS + self.TEMP_ANIMALS
      convos = self.TEMP_CONVOS

      # Pick two animals and make sure they're not the same one
      to = random.choice(all_animals)
      fro = random.choice(all_animals)
      while fro == to:
         fro = random.choice(all_animals)

      # Check to make sure the these two animals didn't have a conversation already (or at least the "to"
      # animal didn't already initiate a conversation with the "from" animal
      already = False
      if to['name']+to['animal'] in convos.keys():
         if fro['name']+fro['animal'] in convos[to['name']+to['animal']]:
            already = True

      # If this is a new conversation, continue
      if not already:
         self.TEMP += "\n" + to['name'] + ' asked ' + fro['name'] + ', "What exactly are you?"\n'
         self.TEMP += "\"Well, I'm " + referenced(fro['animal'])

         # If the "fro" animal has some properties in ConceptNet, print one randomly
         if "HasProperty" in self.ANIMAL_CONCEPTS[fro['animal']].keys():
            self.TEMP += " and I'm " + self.clean_phrase(singularize(random.choice(self.ANIMAL_CONCEPTS[fro['animal']]['HasProperty'])))

         self.TEMP += "."

         # If the "fro" animal has a "HasA" relationship in ConceptNet, print one randomly
         hasa = False
         if "HasA" in self.ANIMAL_CONCEPTS[fro['animal']].keys():
            has = referenced(singularize(random.choice(self.ANIMAL_CONCEPTS[fro['animal']]['HasA'])))
            self.TEMP += " I have " + self.clean_phrase(has)
            hasa = True

         # If the "fro" animal is capable of something, talk about it
         capable = False
         if "CapableOf" in self.ANIMAL_CONCEPTS[fro['animal']].keys():
            capable = True
            ability = random.choice(self.ANIMAL_CONCEPTS[fro['animal']]['CapableOf'])

            # Sometimes the "CapableOf" relationship in ConceptNet is negated, so make 
            # sure we have consistent logic
            can = "can"
            if ability.find("cannot ") == 0:
               can = "cannot"
               ability.replace("cannot ", "")

            if hasa:
               self.TEMP += " and"

            # State the ability and ask the "to" animal if they can do the same thing
            self.TEMP += " I " + can + " " + self.clean_phrase(ability) + ", can you?"

         if hasa and not capable:
            self.TEMP += "."

         self.TEMP += "\"\n"

         # If there was a stated ability for the "fro" animal
         if capable:

            # Check to see if the "to" animal also has the same ability, and if so say so
            canto = False
            if 'CapableOf' in self.ANIMAL_CONCEPTS[to['animal']].keys():
               if ability in self.ANIMAL_CONCEPTS[to['animal']]['CapableOf']:
                  canto = True
                  self.TEMP += '"Yes I can!"'

            # If not, say so
            if not canto:
               self.TEMP += '"No I can' + "'t"

               # If they have other abilities, though, pick one and print it
               if 'CapableOf' in self.ANIMAL_CONCEPTS[to['animal']].keys():
                  self.TEMP += ", but I do know how to " + self.clean_phrase(random.choice(self.ANIMAL_CONCEPTS[to['animal']]['CapableOf'])) + "!"
               else:
                  self.TEMP += ","

            self.TEMP += '" replied ' + to['name'] + ".\n"

         # Add the conversation to the list
         if to not in self.TEMP_CONVOS.keys():
            self.TEMP_CONVOS[to['name']+to['animal']] = []

         self.TEMP_CONVOS[to['name']+to['animal']].append(fro['name']+fro['animal'])

   # -------------------------------------------------------------------------------------------------------------
   def unfollow(self):
      """Loop through the following animals list and randomly pick some to remove"""

      # There's a percentage chance an animal may unfollow the narrator. Check for that,
      # remove the animal from the list and add it to an unfollow list
      unfollowed = []
      for a in self.ANIMALS:
         if random.randrange(100) < 3:
            unfollowed.append(a)
            self.ANIMALS.remove(a)

      # Loop through the unfollow list building a textual representation of the animals that 
      # unfollowed. Return that string
      temp = ""
      for a in unfollowed:
         if a == unfollowed[-1] and len(unfollowed) > 1:
            temp += ", and "
         elif a != unfollowed[0]:
            temp += ", "

         temp += a['name'] + " the " + a['animal']

      if temp:
         temp += " stopped following me for some reason.\n"

      return temp

   # -------------------------------------------------------------------------------------------------------------
   def count_words(self):
      """Returns the current number of words in the text"""

      return len(re.split(r'[^0-9A-Za-z]+', self.full_text()))

   # -------------------------------------------------------------------------------------------------------------
   def clean_phrase(self, str):
      """Cleans concept phrase for printing"""

      return str.replace("_", " ")

   # -------------------------------------------------------------------------------------------------------------
   def get_animal_concepts(self, animal):
      """Queries ConceptNet for data on a particular animal"""

      # ConceptNet API: https://github.com/commonsense/conceptnet5/wiki/API
      if animal not in self.ANIMAL_CONCEPTS.keys():
         r = requests.get(CONCEPTNET_URL + animal)

         if r.json():
            rels = {}

            # For each edge found, save each "end" in a list of "rels"
            for e in r.json()['edges']:
               rel = e['rel'].split('/')[-1]
               end = e['end'].split('/')[-1]

               if len(end.split('_')) <= 2 and end != animal:
                  if rel not in rels.keys():
                     rels[rel] = []

                  rels[rel].append(end)

            self.ANIMAL_CONCEPTS[animal] = rels

      # Cache all current concepts found after each pull from the ConceptNet API
      f = open('concepts.json', 'w')
      f.write(json.dumps(self.ANIMAL_CONCEPTS))
      f.close()

   # -------------------------------------------------------------------------------------------------------------
   def get_animals_following(self):
      """Retrieve a textual list of animals currently following the narrator"""

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

   # -------------------------------------------------------------------------------------------------------------
   def get_flowers_held(self):
      """Get a textual representation of flowers currently held by the narrator"""

      if self.FLOWERS:
         if not self.ANIMALS:
            self.TEXT += "So far "

         self.TEXT += "I held " + numerals(len(self.FLOWERS)) + " flower"

         if len(self.FLOWERS) > 1:
            self.TEXT += "s"

         self.TEXT += ". "

      self.TEXT += "\n"

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

            temp += a['name'] + " the " + a['animal']

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

            temp += referenced(f['color'] + " " + f['flower'])

      return temp + ".\n"

   # -------------------------------------------------------------------------------------------------------------
   def full_text(self):
      """Returns the full text of the novel as a string"""

      return self.TITLE + "\n" + self.get_prologue() + self.TEXT + self.get_afterword()

   # -------------------------------------------------------------------------------------------------------------
   def write_html(self):
      """Builds HTML version of the book"""

      html  = "<!DOCTYPE html>\n"
      html += "<html>\n"
      html += "<head>\n"
      html += "<title>Flora and Fauna</title>\n"
      html += '<meta charset="UTF-8">\n'
      html += '<link rel="stylesheet" href="css/main.css" type="text/css">\n'
      html += "</head>\n"
      html += "<body>\n"

      html += "<h1>Flora and Fauna</h1>\n"

      # Replace the tildas with <h2>
      prologue = re.sub(r'~~~ PROLOGUE ~~~', '<h2>PROLOGUE</h2>', self.get_prologue()).split("\n")
      for line in prologue:
         if line == prologue[0]:
            html += line + "\n"
         else:
            html += "<div>" + line + "</div>\n"

      # Loop through all the text and add maps at chapter start
      chapter = 1
      for line in self.TEXT.split("\n"):

         image = ""

         # Replace tildas with <h3>, start chapter
         if line[:3] == "~~~":
            html += '<hr>\n'
            image = '<div class="map"><img class="map_image" src="maps/' + str(chapter) + '.png" alt="Maze ' + str(chapter) + '"></div>\n'
            chapter += 1
         else:
            line = "<div>" + line + "</div>\n"

         line = re.sub(r'^~~~ ', '<h2>', line)
         line = re.sub(r' ~~~$', '</h2>', line)
         html += line

         html += image

         if not line: 
            logging.info('-----NONE------')

      # Replace afterword tildas as before, and add it to HTML string
      afterword = re.sub(r'~~~ AFTERWORD ~~~', '<h2>AFTERWORD</h2>', self.get_afterword()).split("\n")
      for line in afterword:
         if line == afterword[1] or line == afterword[-2]:
            line = re.sub(r'^THE END$', '<h2>THE END</h2>', line)

            html += line + "\n"
         else:
            html += "<div>" + line + "</div>\n"

      html += "</body>\n"
      html += "</html>\n"

      # Write HTML to file
      f = open("html/index.html", "w")
      f.write(html)
      f.close()

   # -------------------------------------------------------------------------------------------------------------
   def write_text(self):
      """Writes the TEXT attribute out to a file"""

      text = ""

      # Loop through the lines and wrap those over 80 characters
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

      # Write it to file
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

   # Keep building and traversing mazes until we have enough words
   bad = 0
   last = j.CHAPTER
   while j.count_words() < 50000:
      j.build_maze()
      j.traverse_maze()

      if j.CHAPTER == last:
         j.IMAGE.writePng("html/bad/" + str(j.CHAPTER) + "_" + str(bad) + ".png")

         f = open("html/bad/" + str(j.CHAPTER) + "_" + str(bad) + ".txt", "w")
         f.write(j.DEBUG)
         f.close()

         bad += 1

      last = j.CHAPTER

   # Write the results out
   j.write_html()
   j.write_text()

   logging.info('Done, with ' + str(j.count_words()) + ' words')

# -------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   sys.exit(main())
