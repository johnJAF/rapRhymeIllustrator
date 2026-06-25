# for web scraping
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
# parsing for links to make sure links are links
from urllib.parse import urlparse
# regex parsing
import re
# struct
from dataclasses import dataclass, field

phonemes = {} # dicionary for the phonemes dict that is in the .txt files

allWords = [] # list of all the words that the lyricsholder will be turned into

# i want to build this as a struct python classes are goofy to me
@dataclass
class WordData:
    original_word: str # "beat"
    phonemes: str      # "B IY1 T"
    rhyme_tail: str    # "IY1 T"
    line_number: int   # 3
    word_in_line: int  # 2
    global_position: int # 15
    
    is_rhyme: bool = False # marked true at all if this word rhymes with ANYTHING, default false
    rhymes_with: set = field(default_factory=set) # this is a set for each object that holds rhyme-cousins (default factory calls set for each obj)

# load up all of the dictionary words into a python dictionary
def loadDicitonary():
    with open("cmudict_SPHINX_40.txt", "r") as f:
        delimited = ""
        
        for line in f:
            if line == "":
                continue
            
            delimited = line.split(maxsplit=1) # for each line were going to split it at exactly its delimiter ONLY once
            
            phonemes[delimited[0]] = delimited[1].strip() # add each split line into dictionary, strip removes the \n at the end of each word
        
# function for grabbing web scrape from azlyrics
def azLyricScrape(link):
    # just in case link passes all checks but isnt actuall an azlyrics link 
    if "https://www.azlyrics.com/lyrics" not in link:
        print("this is not valid")
        return
    
    response = requests.get(link) # opening up response again in order to actually pull the html of the specific website we want up
    
    # soup contains the entire website html
    soup = BeautifulSoup(response.text, 'html.parser')
    
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    
    textFromWebsite = ""
    
    # finding the div where the actual lyrics are (because its unmarked we have to go by comment and this comment shows up every time over the lyrics)
    for comment in comments:
        if "Usage of azlyrics.com content" in comment:
            textFromWebsite = comment.parent.text.strip() # this skips all the html bs and gets ONLY the text
        elif "Bot Ban" in comment: 
            print("your access is flagged bc you spammed the website too much")
        else: 
            print("this is not pulling the right web page")
            return ""
            
    # now that we have the actual lyrics, lets parse the lyrics so we can genuinely get what we need.
    lyricsOnly = re.sub("\\[.+?\\]", "", textFromWebsite) # .+? is telling regex "any block of text with any thing in between [ and ] is fair game to remove"
    lyricsOnly = re.sub("\\(.+?\\)", "", lyricsOnly)
    
    listOfLines = lyricsOnly.splitlines() # turns string into list of lines
    
    betterListOfLines = [line for line in listOfLines if line != ""] # hey i dont want anything "" related
    
    saveToTxt(betterListOfLines) # doing this for debugging purposes, i think it would be more optimal to just keep this list in memory to iteratively go over it and such
    
    return betterListOfLines

# this funciton assumes that you dont want to enter a link and your lyricsholder.txt is formatted as such:
    # lyrics only
    # (\n) line breaks for each direct song line
    # can have adlibs but preferred if removed
    # should work for copy and paste from most lyric websites
def scrapeFromTxtOnly():
    listOfLines = []
    
    # loading local file
    with open("lyricsholder.txt", "r") as f:
        for line in f:
            line = re.sub("\\[.+?\\]", "", line) # should remove any [ ] enclosed text as the line comes in
            line = re.sub("\\(.+?\\)", "", line) # should remove any adlibs or things enclsoed in ( )
            listOfLines.append(line.strip())
            continue
    
    betterListOfLines = [line for line in listOfLines if line != ""] # hey i dont want anything "" related
    
    saveToTxt(betterListOfLines) # doing this for debugging purposes, i think it would be more optimal to just keep this list in memory to iteratively go over it and such
    
    return betterListOfLines


# assumes that allWords the list full of word objects is full of properly scraped words, if word is NA it just doesn't get checked as a rhyme
# a rhyme is decided within a sliding window of 31 words where the ten words before or after of word are checked by endRhyme to decide rhyme-ability
def lookForRhymes():
    LIMIT = 15
    
    # for index 0 in total indexes of allWords
    for x in range(len(allWords)-1): 
        print("Loop one")
        
        if allWords[x].original_word == "NA": # we will not check any direction for words that are not known
            continue
        
        currentRhymeTail = allWords[x].rhyme_tail
        
        # left check
        backwardsWalk = x
        
        # this mini loop should run until we reach LIMIT, which would be 15 steps back or 0
        while (backwardsWalk > 0) and (not x - backwardsWalk == LIMIT): 
            print("Loop two")
            backwardsWalk -= 1 # since we're not at 0, lets take a looksy
            
            if allWords[backwardsWalk].original_word == "NA": 
                continue
            
            backwardTail = allWords[backwardsWalk].rhyme_tail
            
            # should there be some kind of confidence calculation? because TBH i feel like comparing apples to apples is fine
            # until we have near-rhymes and then its kinda meh but how would we even decide near-rhymes without doing some typa voodoo
            
            if currentRhymeTail == backwardTail: # rhyme spotted
                print(f"rhyme spotted: {currentRhymeTail}")
                print(type(allWords[x].rhymes_with))

                print(allWords[x].rhymes_with)
                # we just knocked two birds with one stone
                # bc these are added to sets we enjoy not worrying abt duplicates down the line (i think)
                allWords[x].is_rhyme = True
                allWords[x].rhymes_with.add(allWords[backwardsWalk].global_position) # assuming that this is a set pls remmeber to change
                
                allWords[backwardsWalk].is_rhyme = True
                allWords[backwardsWalk].rhymes_with.add(allWords[x].global_position)
            else:
                continue
            
        for word in allWords:
            print(f'Word: {word.original_word}, rhymes: {word.is_rhyme}, rhymes_with: {word.rhymes_with} \n')
        
        # right check
        
        

# assumes word is a word, and has a phonetic translation
def createWordDataObject(word, phoneticVersion, tail, lineNumber, wordInLine, globalPosition):
    word = WordData(word, phoneticVersion, tail, lineNumber, wordInLine, globalPosition) 
    
    allWords.append(word)

def isInCMU(word)->bool:
    if word in phonemes:
        return True
    
def grabEndRhyme(phoneticVersion):
    phonemes = ""
    phonemes = phoneticVersion.split()
    
    endRhyme = ""
    # work backwards from the phonemes because well be able to find the last stressed vowel 
    # last stressed vowel matters because thats usually what part of the word is rhymed with
    # if we keep that we get to see the end-rhyme
    for x in range(len(phonemes) - 1, -1, -1): 
        if "1" in phonemes[x] or "2" in phonemes[x]: # if we find where the last-stressed-vowel is
            endRhyme = phonemes[x:] # grab the phonemes from the LSV to the end
            
    return endRhyme

# assumes that the phonemes are already loaded and that the lyrics have already been processed for phonetification (not a word?)
def turnLyricsToPhonetic(listOfLyrics):
    lineNumber = 0
    globalPosition = 0
    # first grab a line from the song
    for line in listOfLyrics:
        # split that line into words
        words = ""
        words = line.split()
        for word in words:
            word = word.upper().strip("!?.,;():-\"")
            wordInLine = 0
            
            while True: # loop is for re-checking if new generated word is fit for CMU
                if isInCMU(word): # only passes a word through if its immediately a dictionary entry
                    endRhyme = grabEndRhyme(phonemes[word])
                    createWordDataObject(word, phonemes[word], endRhyme, lineNumber, wordInLine, globalPosition)
                elif "-" in word: # generally i assume the ladder half of a hyphenated word is the rhyming portion, that becomes the new word
                    hyphenatedSplit = word.split("-")
                    rhymingPortion = hyphenatedSplit[1]
                    
                    word = rhymingPortion # ex: if the word was hip-hop, youd restart the conditional check with "hop" instead of hip-hop
                    continue
                else: # word is not immediately findable
                    createWordDataObject("NA", word, "NA", lineNumber, wordInLine, globalPosition)
                    
                wordInLine += 1
                globalPosition += 1 # tells us which word exactly in the grand scheme of the lyrics we're at
                break
        lineNumber += 1 # tells us what line (within the verses) we're at
        
# save to a txt file
def saveToTxt(listOfLyrics):
    # i have to do this bs to remove blanks bc splitlines doesnt just skip blanks 
    with open("lyricsholder.txt", "w") as f:

        for line in listOfLyrics:
            if line == "":
                continue
            else:
                f.write(line + "\n")
                continue
    
# grab da link
def grabDaLink():
    linkString = ""
    while(True):
        linkString = input("What link would you like to use? \n").lower().strip()
        print("\n \n")
        
        linkObject = urlparse(linkString) # this should turn link into a urlparse object which would allow us to actually parse it as a URL
        
        # check if link is an actual link at all
        if linkObject.scheme and linkObject.netloc:
            # now lets check if the website exists at all
            response = requests.get(linkString)
            
            if response.status_code == 200: # 200 = successful website request
                #print("this link si real and the website exists")
                return linkString
            else:
                print("this link does not exist")
                continue
        else:
            print("this is not a link")
            continue  
        
# goal for main function (for now): 
    # call on funciton to grab from azlyrics
    # ask user for link
    # azlyric function spits out a .txt where we get all of the websites data
    # main will look at such txt and print it out
def main():
    loadDicitonary()
    
    #link = grabDaLink()
    
    # i could probably add some like link checker so for ex: if its a azlyrics link then we go to that fucntion
    # if we figure genius out we could go there too
    # if its an apple or spotify api we can figre that out IDK
    
    #listOfLyrics = azLyricScrape(link) 
    listOfLyrics = scrapeFromTxtOnly()
    
    turnLyricsToPhonetic(listOfLyrics)
    
    lookForRhymes()
    
    #print(allWords)
    
    

if __name__ == "__main__":
    main()
