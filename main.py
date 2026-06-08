# shi for web scraping
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
# parsing for links to make sure links are links
from urllib.parse import urlparse

# function for grabbing web scrape from azlyrics
def azLyricScrape(link):
    # just in case link passes all checks but isnt actuall an azlyrics link 
    if "https://www.azlyrics.com/lyrics" not in link:
        print("this shit is not valid")
        return
    
    response = requests.get(link) # opening up response again in order to actually pull the html of the specific website we want up
    
    # soup contains the entire website html
    soup = BeautifulSoup(response.text, 'html.parser')
    
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if "Usage of azlyrics.com content" in comment:
            print(comment.parent.prettify())
    
# grab da link
def grabDaLink():
    linkString = ""
    while(True):
        linkString = input("What link would you like to use? \n").lower().strip()
        
        linkObject = urlparse(linkString) # this should turn link into a urlparse object which would allow us to actually parse it as a URL
        
        # check if link is an actual link at all
        if linkObject.scheme and linkObject.netloc:
            # now lets check if the website exists at all
            response = requests.get(linkString)
            
            if response.status_code == 200: # 200 = successful website request
                print("this link si real and the website exists")
                return linkString
            else:
                print("this link does not exist")
                continue
        else:
            print("this shi is not a link")
            continue  
        
# goal for main function (for now): 
    # call on funciton to grab from azlyrics
    # ask user for link
    # azlyric function spits out a .txt where we get all of the websites data
    # main will look at such txt and print it out
def main():
    link = grabDaLink()
    
    azLyricScrape(link)
    
if __name__ == "__main__":
    main()
