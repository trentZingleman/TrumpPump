import shutil
import os
import codecs
import glob
import re
import requests
from tqdm import tqdm
from datetime import datetime
import calendar
import time
from math import ceil
import json

def createFilename(filename):
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    alphabetPos = 0
    isFirst = True
    while os.path.isfile('../Data/Sorted/' + filename + '.txt'):
        #the file already exists, so lets add a letter to keep it in order
        if isFirst:     #this is the first copy of the file
            filename += alphabet[alphabetPos]
            isFirst = False
        else:       #this is not the first copy of the file so iterate down the alphabet to keep it in order
            filename = filename[:-1] + alphabet[alphabetPos]
        alphabetPos += 1
    return '../Data/Sorted/' + filename + '.txt'

#retreive all links of Trump's public speeches
def getLinks():
    baseUrl = 'https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=200301&category2%5B0%5D=65&category2%5B1%5D=64&category2%5B2%5D=55&category2%5B3%5D=52&category2%5B4%5D=74&category2%5B5%5D=78&category2%5B6%5D=76&category2%5B7%5D=51&category2%5B8%5D=57&category2%5B9%5D=49&category2%5B10%5D=48&category2%5B11%5D=8&category2%5B12%5D=54&category2%5B13%5D=68&items_per_page=100&page='
    
    searchResults = []
    while len(searchResults) == 0:      #sometimes the wont respond to the search results so try until a we get a proper responce:
        searchResults = re.findall(r'(?<=<h3><span>Results</span>&nbsp;&nbsp; 1 - 100 of )[^ ]*', requests.get(baseUrl + '0').text)
    pages = ceil(int(searchResults[0])/100)     #figure out how many pages of search results we have to iterate through

    links = []
    for pagenum in tqdm(range(pages), "Scraping hyperlinks to Donald Trump's public speeches"):
        htmlData = requests.get(baseUrl + str(pagenum)).text            #get the raw HTML of the query
        htmlData = htmlData.split('</thead>')[1]                        #remove everything above the section that contains the links we want
        htmlData = htmlData.split('<div class=\"text-center\">')[0]     #remove everything below the section that contains the links we want
        htmlData = htmlData.replace('<a href=\"/people/president/donald-j-trump\">Donald J. Trump</a>','')      #remove all instances of this hyperlink so the only ones left are the ones we want
        links += [link for link in re.findall(r'(?<=<a href=")[^"]*', htmlData) if 'notice' not in link and 'joint-statement' not in link]            #now extract all links to Trump's public speeches and add them to the list, excluding notices
    links.append('/documents/address-before-joint-session-the-congress-the-state-the-union-26')     #adding this too, it didnt get found in the search query apparently
    return links


def scrape(links):
    baseUrl = 'https://www.presidency.ucsb.edu'
    filterToArticle = re.compile('<div class="field-docs-content">(.*?)</div>', re.DOTALL)
    peopleCounter = re.compile(r'<([a-z]{1,6})>(?i:PRESIDENT DONALD TRUMP|The President|President Trump)[.:]*\s?</\1>[.:]*')
    htmlCleaner = re.compile(r'(<(([a-z]{1,6}[^>]+)|(/span)|([/]?p))> *)|( *[\(\[].*?[\)\]] *)')
    for i, link in tqdm(enumerate(links), desc="Scraping Data From Links", total=len(links)):   
        htmlData = requests.get(baseUrl + link).text
        articleTime = re.findall(r'(?<=<span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content=")[^+]*', htmlData)[0]  #get time of article
        epochArticleTime = calendar.timegm(time.strptime(articleTime, '%Y-%m-%dT%H:%M:%S'))     #convert article time to time since epoch
        filename = createFilename(str(epochArticleTime))
        with codecs.open(filename, 'w', encoding='utf8') as outfile: 
            htmlData = filterToArticle.search(htmlData).groups()[0]     #we are grabbing the text of the article itself
            htmlData = htmlCleaner.sub('', htmlData)        #this cleans out HTML tags that we dont want
            
            foundPeople = peopleCounter.search(htmlData)    #check to see if Trump is the only one talking or not
            if foundPeople is not None:
                #here we know there are multiple talking within the transcript and must find the identifier tags
                trumpTag = foundPeople.group(1)
                htmlData = re.sub(r'<[/]?([a-z]{1,6})(?<!' + re.escape(trumpTag) + r')>', '', htmlData)      #remove all tags that dont indicate that a new person is talking
                trumpIdentifier = '<' + trumpTag + '>TRUMPBOI:</' + trumpTag + '>'
                htmlData = peopleCounter.sub(trumpIdentifier, htmlData)     #we label everywhere trump speaks as 'TRUMPBOI'
                htmlData = re.sub('<' + trumpTag + '>', '\n<' + trumpTag + '>', htmlData)       #we are giving every speaker their own line for cleanliness
                htmlData = re.sub('<' + trumpTag + '>Crowd</' + trumpTag + '>.*[\n](?!<' + trumpTag + '>)', '', htmlData)       #sometimes when they include the crowd, they dont terminate it correctly so this is a fix for that
                htmlData = re.sub('<' + trumpTag + '>.*[^.:]\s?</' + trumpTag + '>[^.:]', '', htmlData)     #sometimes they have descriptions using the same tas as talking people which screws things up so this is a fix for that
                htmlData = ''.join(re.findall(r'(?<=' + re.escape(trumpIdentifier) + ')[^<]*', htmlData))   #only grab stuff spoken by trump himself
            else:
                #here we know that trump is the only one talking so we only need to clean the HTML tags out of the text
                htmlData = re.sub(r'<[/]?[a-z]{1,6}>', '', htmlData)
            
            htmlData = re.sub(r'(\n)|(\s{2,})', ' ', htmlData)       #remove the spaces
            outfile.write(' %s ' %(htmlData))


def readTweets():
    with open('../Data/tweets/trumpTweets.JSON') as infile:
        data = json.load(infile)
        for tweet in tqdm(data["tweets"], desc="Reading Donald Trump's Tweets"):
            epochTweetTime = calendar.timegm(time.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y'))     #convert article time to time since epoch
            filename = createFilename(str(epochTweetTime))
            with codecs.open(filename, 'w', encoding='utf8') as outfile:
                outfile.write(' %s ' %(re.sub(r"http\S+", "", tweet["text"])))


def combineAll():
    with codecs.open('../Data/tempfile.txt', 'wb', encoding='utf8') as outfile:
        with codecs.open('../Data/beforePresidency/trump_pre_election_speeches.txt', 'rb', encoding='utf8') as firstfile:
            shutil.copyfileobj(firstfile, outfile)
        for filename in tqdm(glob.glob('../Data/Sorted/*.txt'), desc='Combining Data In Order'):
            with codecs.open(filename, 'rb', encoding='utf8') as readfile:
                shutil.copyfileobj(readfile, outfile)

    with codecs.open('../Data/trump_data_full.txt', 'wb', encoding='utf8') as outfile:
        with codecs.open('../Data/tempfile.txt', 'rb', encoding='utf8') as infile:
            data = infile.read()
            data = re.sub(r'(AUDIENCE MEMBER:).*(MR. TRUMP:)', '', data)
            data = re.sub(r'(DONALD TRUMP)( JR)?', '', data)
            #data = re.sub(r'([ ]*--[ ]*){2,}', ' -- ', data)
            data = re.sub(r'&amp;', '', data)
            #data = re.sub(r'[? ]{2,}', ' ', data)
            #data = re.sub(r'[. ]{3,}', '... ', data)
            data = re.sub(r'[^\w\s]','',data)
            data = re.sub(r'(\n)|(\s{2,})', ' ', data)
            outfile.write('%s' %(data.lower()))

def cleanUp():
    dataFiles = glob.glob('../Data/Sorted/*')
    for file in tqdm(dataFiles, desc='Cleaning Up'):
        os.remove(file)
    os.remove('../Data/tempfile.txt')
    os.rmdir('../Data/Sorted')

if __name__ == "__main__":
    os.makedirs("../Data/Sorted")
    links = getLinks()
    scrape(links)
    readTweets()
    combineAll()
    cleanUp()