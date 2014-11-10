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
   CONVOS = {}
   TEMP_ANIMALS = []
   TEMP_CONVOS = {}
   ANIMAL_CONCEPTS = {}

   COLORS = {}

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

      next = None

      # Keeps track of valid directions to go from 'here' (unvisited squares)
      dirs = []

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

      else:
         if j - 1 >= 0:
            if self.MAZE[i][j - 1]['s'] and not self.MAZE[i][j - 1]['v']:
               dirs.append('n')

         if j + 1 < self.MAZE_SIZE:
            if self.MAZE[i][j + 1]['n'] and not self.MAZE[i][j + 1]['v']:
               dirs.append('s')

         if i + 1 < self.MAZE_SIZE:
            if self.MAZE[i + 1][j]['w'] and not self.MAZE[i + 1][j]['v']:
               dirs.append('e')

         if i - 1 >= 0:
            if self.MAZE[i - 1][j]['e'] and not self.MAZE[i - 1][j]['v']:
               dirs.append('w')

      if len(dirs):
         # Pick a random direction and update the current square's visited flag and the wall flag in that direction
         dir = random.choice(dirs)
         # logging.info("Found next square from (" + str(i) + "," + str(j) + ") in direction " + dir)
         self.MAZE[i][j][dir] = 1

         # Find the next square in the random direction and update those flags, too
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

      then = False

      total = 0
      last_dir = ''
      last_i = -1
      last_j = -1
      # Run through the maze 
      while (len(stack)):

         i = square['i']
         j = square['j']

         # Get a random neighbor that hasn't been visited
         next = self.next_maze(i, j)

         # If one was found, add it to the stack and flip its visited flag
         if next:
            first_dead_end = True

            last_i = i
            last_j = j

            self.MAZE[i][j]['v'] = 1

            i = next[0]
            j = next[1]

            self.MAZE[i][j]['v'] = 1
            square = {'i': i, 'j': j}

            if next[2] in ['e', 'w']:
               self.IMAGE.filledRectangle((last_i * 15 + 7, last_j * 15 + 6), (i * 15 + 7, j * 15 + 8), self.COLORS['green'])
            else:
               self.IMAGE.filledRectangle((last_i * 15 + 6, last_j * 15 + 7), (i * 15 + 8, j * 15 + 7), self.COLORS['green'])

            # If we found an exit!
            if self.MAZE_EXIT['i'] == i and self.MAZE_EXIT['j'] == j:
               self.CHAPTER += 1
               
               self.IMAGE.writePng("html/maps/" + str(self.CHAPTER) + ".png")

               self.TEXT += "~~~ CHAPTER " + numerals(str(self.CHAPTER)).upper() + " ~~~\n"
               self.TEXT += self.TEMP
               self.TEXT += "Then I " + random.choice(self.WALK) + " down a flight of stairs. "

               self.FLOWERS += self.TEMP_FLOWERS
               self.ANIMALS += self.TEMP_ANIMALS
               
               for c in self.TEMP_CONVOS:
                  if c not in self.CONVOS.keys():
                     self.CONVOS[c] = []

                  self.CONVOS[c].append(self.TEMP_CONVOS[c])

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

                  self.IMAGE.filledRectangle((i * 15 + 3, j * 15 + 3), (i * 15 + 5, j * 15 + 5), self.COLORS['purple'])

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
                  then = False

               # Or is there an animal here?
               elif random.randrange(100) < 5:
                  animal = random.choice(self.JSON['animals'])
                  name = random.choice(self.JSON['names'])

                  self.TEMP += "There was " + referenced(animal) + " there. "
                  self.TEMP += "I named it " + name + "."

                  self.IMAGE.filledRectangle((i * 15 + 3, j * 15 + 9), (i * 15 + 5, j * 15 + 11), self.COLORS['red'])

                  # Did the animal follow the narrator?
                  if random.randrange(100) < 10:
                     self.TEMP_ANIMALS.append({'name': name, 'animal': animal})

                     self.get_animal_concepts(animal)

                     self.TEMP += " It started following me."

                  self.TEMP += "\n"

                  then = False

               # Or are two animals talking to each other?
               elif random.randrange(100) < 1 and len(self.ANIMALS) + len(self.TEMP_ANIMALS) > 1:
                  all_animals = self.ANIMALS + self.TEMP_ANIMALS
                  convos = self.TEMP_CONVOS

                  to = random.choice(all_animals)
                  fro = random.choice(all_animals)
                  while fro == to:
                     fro = random.choice(all_animals)

                  already = False
                  if to['name']+to['animal'] in convos.keys():
                     if fro['name']+fro['animal'] in convos[to['name']+to['animal']]:
                        already = True

                  if not already:
                     self.TEMP += "\n" + to['name'] + ' asked ' + fro['name'] + ', "What exactly are you?"\n'
                     self.TEMP += "\"Well, I'm " + referenced(fro['animal'])

                     if "HasProperty" in self.ANIMAL_CONCEPTS[fro['animal']].keys():
                        self.TEMP += " and I'm " + self.clean_phrase(singularize(random.choice(self.ANIMAL_CONCEPTS[fro['animal']]['HasProperty'])))

                     self.TEMP += "."

                     hasa = False
                     if "HasA" in self.ANIMAL_CONCEPTS[fro['animal']].keys():
                        has = referenced(singularize(random.choice(self.ANIMAL_CONCEPTS[fro['animal']]['HasA'])))
                        self.TEMP += " I have " + self.clean_phrase(has)
                        hasa = True

                     capable = False
                     if "CapableOf" in self.ANIMAL_CONCEPTS[fro['animal']].keys():
                        capable = True
                        ability = random.choice(self.ANIMAL_CONCEPTS[fro['animal']]['CapableOf'])

                        can = "can"
                        if ability.find("cannot ") == 0:
                           can = "cannot"
                           ability.replace("cannot ", "")

                        if hasa:
                           self.TEMP += " and"

                        self.TEMP += " I " + can + " " + self.clean_phrase(ability) + ", can you?"

                     if hasa and not capable:
                        self.TEMP += "."

                     self.TEMP += "\"\n"

                     if capable:
                        canto = False
                        if 'CapableOf' in self.ANIMAL_CONCEPTS[to['animal']].keys():
                           if ability in self.ANIMAL_CONCEPTS[to['animal']]['CapableOf']:
                              canto = True
                              self.TEMP += '"Yes I can!"'

                        if not canto:
                           self.TEMP += '"No I can' + "'t"

                           if 'CapableOf' in self.ANIMAL_CONCEPTS[to['animal']].keys():
                              self.TEMP += ", but I do know how to " + self.clean_phrase(random.choice(self.ANIMAL_CONCEPTS[to['animal']]['CapableOf'])) + "!"
                           else:
                              self.TEMP += ","

                        self.TEMP += '" replied ' + to['name'] + ".\n"


                     if to not in self.TEMP_CONVOS.keys():
                        self.TEMP_CONVOS[to['name']+to['animal']] = []

                     self.TEMP_CONVOS[to['name']+to['animal']].append(fro['name']+fro['animal'])

               self.MAZE[i][j]['v'] = 1
               self.MAZE[i][j][next[2]] = 1

               stack.append({'i': i, 'j': j})
               total += 1

               last_dir = self.OPPOSITE[next[2]]

         # Or if there are no valid directions, step back through the path to get to a square with
         # unvisited neighbors
         else:
            if first_dead_end:
               self.TEMP += "Then I hit a dead-end. I was feeling lost so I retraced my steps.\n"
               then = False
               first_dead_end = False


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

      if animal not in self.ANIMAL_CONCEPTS.keys():
         r = requests.get(CONCEPTNET_URL + animal)

         if r.json():
            rels = {}

            for e in r.json()['edges']:
               rel = e['rel'].split('/')[-1]
               end = e['end'].split('/')[-1]

               if len(end.split('_')) <= 2 and end != animal:
                  if rel not in rels.keys():
                     rels[rel] = []

                  rels[rel].append(end)

            self.ANIMAL_CONCEPTS[animal] = rels

      f = open('concepts.json', 'w')
      f.write(json.dumps(self.ANIMAL_CONCEPTS))
      f.close()

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
      html += '<link rel="stylesheet" href="css/main.css" type="text/css">'
      html += "</head>\n"
      html += "<body>\n"

      html += "<h1>Flora and Fauna</h1>\n"

      prologue = re.sub(r'~~~ PROLOGUE ~~~', '<h2>PROLOGUE</h2>', self.get_prologue()).split("\n")
      for line in prologue:
         if line == prologue[0]:
            html += line
         else:
            html += "<div>" + line + "</div>"

      chapter = 1
      for line in self.TEXT.split("\n"):
         image = ""
         if line[:3] == "~~~":
            html += '<hr>'
            image = '<div class="map"><img class="map_image" src="maps/' + str(chapter) + '.png" alt="Maze ' + str(chapter) + '"></div>'
            chapter += 1
         else:
            line = "<div>" + line + "</div>"

         line = re.sub(r'^~~~ ', '<h2>', line)
         line = re.sub(r' ~~~$', '</h2>', line)
         html += line

         html += image

         if not line: 
            logging.info('-----NONE------')

      afterword = re.sub(r'~~~ AFTERWORD ~~~', '<h2>AFTERWORD</h2>', self.get_afterword()).split("\n")
      for line in afterword:
         if line == afterword[1] or line == afterword[-2]:
            line = re.sub(r'^THE END$', '<h2>THE END</h2>', line)

            html += line
         else:
            html += "<div>" + line + "</div>"

      html += "</body>\n"
      html += "</html>\n"

      f = open("html/index.html", "w")
      f.write(html)
      f.close()

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

   j.write_html()
   j.write_text()

   logging.info('Done, with ' + str(j.count_words()) + ' words')

# -------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   sys.exit(main())
