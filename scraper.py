import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict
import tokenizer
import json

global uniquePages
uniquePages = set() # changed form list to a set
global longestPage
longestPage = ("Nothing", 0) #two tuple, first is page and second is length
global wordCounts
wordCounts = defaultdict(int)
global icsSubDomains
icsSubDomains = defaultdict(int)
global dupCheck
dupCheck = set()
global jsonDict
jsonDict = {}


def createJson():
    global uniquePages

    global longestPage

    global wordCounts

    global icsSubDomains

    global dupCheck

    global jsonDict
    jsonDict["UPages"] = list(uniquePages)
    jsonDict["LPage"] = longestPage
    jsonDict["wCount"] = wordCounts
    jsonDict["sDomains"] = icsSubDomains

def clearJSON():
    open("data.json",'w').close()
    
def storeData():
    global uniquePages

    global longestPage

    global wordCounts

    global icsSubDomains

    global dupCheck

    global jsonDict
    uniquePages = list(set(uniquePages))
    data = open('data.json', 'w')
    json.dump(jsonDict, data)
    data.close

def readData():
    with open("data.json", "r") as d:
        data = json.load(d)
    with open('output.txt', 'w') as f:
        f.write("===== The Results of the Crawler ! =====\n\n")
        f.write(f"Number of Unique Pages: {len(data['UPages'])}\n")
        f.write(f"Longest Page in Terms of Words: {data['LPage'][0]}\n")
        f.write(f"  # of words: {data['LPage'][1]}\n\n")

        # sorting portion
        #sorts words by frequency
        sorted_words = sorted(data['wCount'], key = lambda x: data['wCount'][x], reverse = True)
        
        #sorts the ics subdomains by name
        sorted_domains = sorted(data['sDomains'], key = lambda x: (x,data['sDomains'][x]))

        f.write("Top 50 words:\n")
        # still have to do a check to make sure everything is sorted
        for word in sorted_words[:50]:
            f.write(f"{word}, = , {data['wCount'][word]}\n")
        f.write("\n")
        f.write(f"ics.uci.edu subdomains:\nCount: {len(data['sDomains'])}\n")
        for url in sorted_domains:
            f.write(f"{url}, {data['sDomains'][url]}\n")

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    global uniquePages

    global longestPage

    global wordCounts

    global icsSubDomains

    global dupCheck

    global jsonDict
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    #error in page
    if resp.status != 200:
        # do we need to check if there's an error then by using resp.error.url ?
        return list()
    
    #too big
    if len(resp.raw_response.content) > 1_200_000:
        return list()
    
    #duplicate check
    if resp.url in dupCheck:
        # would we use resp.url or regular url... not sure what the difference is ( SOLVED )
        return list()
    dupCheck.add(url)
    #maybe more checks?

    webPage = BeautifulSoup(resp.raw_response.content, "html.parser")
    words = tokenizer.tokenize(webPage.text)
    freq = tokenizer.computeWordFrequencies(words)

    #too much repitition
    if (len(freq.keys())+1)/(len(words)+1) <= float(.2):
        return list()
    
    ## WHERE TO START UPDATING VALUES OF LEN UNIQUE ETC.
    
    # do we need to defrag? ADDING UNIQUE PAGES (Question 1)
    new_url = urlparse(url)._replace(fragment="").geturl()
    uniquePages.add(new_url)

    # counting up words (Question 2)
    for token in words:
        wordCounts[token] +=1
    
    #creating tuple for words and url (Question 3)
    if len(words) > longestPage[1]:
        longestPage = (str(url), len(words))

    #adding subdomains here
    if re.match(r".*\.ics\.uci\.edu.*", url):
        icsSubDomains[urlparse(str(url)).hostname] +=1
    
    #return a list of all urls 
    newUrls = []
    for url in webPage.findAll('a'):
        newUrls.append(url.get('href'))
    #maybe add deleting duplicates here?
    return newUrls

#returns true if the given url has a robot text file 
def RobotTXT_exist(url):
    return True

def readRobot(url):
    return

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if not re.match(r".*(.ics.uci.edu/|.ics.uci.edu/|.informatics.uci.edu/|.stat.uci.edu/|)", parsed.netloc):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
