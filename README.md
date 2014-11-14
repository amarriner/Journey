# Journey

*Python script(s) to generate a novel-length (50,000 word) text for [NaNoGenMo 14](https://github.com/dariusk/NaNoGenMo-2014)*

The idea behind this book is the narrator is a scientist exploring a vast network of caves. Each chapter of the book 
represents a tier or floor of this stucture. Each chapter builds a random maze layout and then drops the narrator 
into the maze. They describe the directions they take as they navigate the maze and describe things they see along 
the way. The narrator is ostensibly cataloging flora and fauna.

The script generates the requisite number of words right now, but it's (obviously) pretty repetative. I'm working on 
making it *slightly* more natural as well as adding more optional and random encounters/happenings. As well as, 
perhaps, more complex events occurring in a single square of a given floor.

Currently the narrator has a percent chance of finding either a flower or an animal in a given square. These are pulled from the 
corpora repository. There's also a percent chance that the narrator will either pick up the flower they found, and a chance the 
animal they found will follow them through the maze. Each level there's another chance some animals will stop following the 
narrator. At the end of the story, there will be a list of flowers held and animals currently following the narrator.

It now produces an HTML version of the novel with corresponding map images of each floor. I found that my mapping algorithm 
wasn't actually producing good maps so as I was debugging and fixing that it made sense to be able to see what was going on. So I 
just incorporated that into the novel itself.

[View on GitHub Pages](http://amarriner.github.io/Journey/)

[My NaNoGenMo-2014 Issue](https://github.com/dariusk/NaNoGenMo-2014/issues/22)

**Dependencies and Tools**
 * [corpora](https://github.com/dariusk/corpora)
 * [pattern.en](http://www.clips.ua.ac.be/pages/pattern-en)
 * [ConceptNet](http://conceptnet5.media.mit.edu/)
 * List of Presidents from [govtrack.us](https://www.govtrack.us/developers/api)
 * US Presidents quotes from [here](http://www.lifehack.org/articles/productivity/55-inspiring-quotes-from-presidents-that-will-change-your-life.html)

## Sample PDF Output

In order to produce a more finished version, I saved a run of the novel's HTML output to PDF.

[Sample PDF](http://amarriner.github.io/Journey/Flora%20and%20Fauna.pdf)


## Sample Map Image
![Sample Map Image](https://raw.githubusercontent.com/amarriner/Journey/gh-pages/html/maps/1.png)
