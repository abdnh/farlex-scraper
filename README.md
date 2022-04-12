A Python script to scrape quizzes from [The Farlex Grammar Book](https://www.thefreedictionary.com/The-Farlex-Grammar-Book.htm).

## Usage

```
$ python farlex.py --help
usage: farlex.py [-h] [--page PAGE | --section {1,2,3}]

optional arguments:
  -h, --help         show this help message and exit
  --page PAGE        download a specific page by its URL slug (e.g. Parts-of-Speech)
  --section {1,2,3}  download a whole section by its number (1: Grammar, 2: Punctuation, 3: Spelling and Pronunciation)
```

Quizzes are written in CSV format to the quizzes directory as `(question, answer, page_url)`.
Mainly meant to be imported to [Anki](https://apps.ankiweb.net/).

Downloaded pages are cached in the pages directory.
