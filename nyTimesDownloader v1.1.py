# -*- coding: utf-8 -*-
from urllib2 import urlopen
from json import loads
from calendar import monthrange
import csv
import re

articleAPIKey = '4d3b7e6441c7b9e57bf30ed59a781686:0:73234709'
queryTerm = "Oil Price"
startYear = 2000
endYear = 2000
nBadArticles = 0


# Retrieve one page 
def retrievePageArticles(queryTerm, startDate, endDate, page):
    queryTerm = queryTerm.replace(" ", "+")
    url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?callback=svc_search_v2_articlesearch&q=" + queryTerm +"&begin_date=" + startDate + "&end_date=" + endDate +  "&sort=oldest&page=" + str(page) + "&api-key=" + articleAPIKey
    return loads(urlopen(url).read())


# Retrive one year articles
def retrieveYearlyArticles(queryTerm, year):
    
    yearArticles = []
    for month in range(1, 13):
        nDays = monthrange(year,month)
        nDays = nDays[1]
        startDate = str(year) + str(month).zfill(2) + "01"
        endDate = str(year) + str(month).zfill(2) + str(nDays).zfill(2)
    
        for page in range(0, 100):
            rawArticles = retrievePageArticles(queryTerm, startDate, endDate, page)
            nArticles = len(rawArticles['response']['docs'])
            
            print("Processing Year " + str(year) + ", Month " + str(month) + ", Page " + str(page))

            if nArticles > 0: 
                monthArticles = parse_articles(rawArticles)
                yearArticles = yearArticles + monthArticles
                
            if nArticles < 10:
                break
                
    return yearArticles
    

# Retrieve all required articles
def retrieveArticles(queryTerm, startYear, endYear):
    global nBadArticles
    allArticles = []
    for year in range(startYear, endYear+1):
        allArticles = allArticles + retrieveYearlyArticles(queryTerm, year)
                
    print("Total Bad Articles is " + str(nBadArticles))
    return allArticles


# Parse one article
def parse_articles(articles):
    '''
    This function takes in a response to the NYT api and parses
    the articles into a list of dictionaries
    '''
    global nBadArticles 
    
    news = []
    for i in articles['response']['docs']:
        dic = {}
        
        
        try:
            isGoodArticle = checkArticle(i)
            #isGoodArticle = True
            if (isGoodArticle == False):
                continue
                            
            dic['id'] = i['_id']
            
            dic['headline'] = prepareString(i['headline']['main'])
            
            
            
            #print(i['headline']['main'])
            #print(dic['headline'])
            
            if i['abstract'] is not None:
                dic['abstract'] = prepareString(i['abstract'])
                #dic['abstract'] =  dic['abstract'].lower()
            else:
                dic['abstract'] = ""
                
                            
            if i['lead_paragraph'] is not None:
                dic['lead_paragraph'] = prepareString(i['lead_paragraph'])
            else:
                dic['lead_paragraph'] =""
                
            dic['desk'] = i['news_desk']
            
            dic['date'] = i['pub_date'][0:10] # cutting time of day.
            
            dic['section'] = i['section_name']
            
            if i['snippet'] is not None:
                dic['snippet'] =prepareString(i['snippet'])
            else:
                dic['snippet'] =""
                
            dic['source'] = i['source']
            
            dic['type'] = i['type_of_material']
            
            dic['url'] = i['web_url']
            
            dic['word_count'] = i['word_count']
            
            # locations
            
            locations = []
            for x in range(0,len(i['keywords'])):
                if 'glocations' in i['keywords'][x]['name']:
                    locations.append(i['keywords'][x]['value'])
            dic['locations'] = locations
            
            # subject
            subjects = []
            for x in range(0,len(i['keywords'])):
                if 'subject' in i['keywords'][x]['name']:
                    subjects.append(i['keywords'][x]['value'])
            dic['subjects'] = subjects   
            
            news.append(dic)
        except:
            nBadArticles +=1
            print("An Article Couldn't be Processed (Total " + str(nBadArticles) + ")")
            pass
        
    return(news)
    
def prepareString(stringToFix):
    
    encodingType = "utf8"
    fixedString = stringToFix.lower()
    
    fixedString = reReplace(fixedString, ",", " ")
    fixedString = reReplace(fixedString, "\'s", " ")

    #regex = re.compile(ur"\u00ED",re.UNICODE)
    #fixedString = re.sub(regex, "i",fixedString)
    
    regex = re.compile(ur"’",re.UNICODE)
    fixedString = re.sub(regex, " ",fixedString)
    
    regex = re.compile(ur"‘",re.UNICODE)
    fixedString = re.sub(regex, " ",fixedString)   
    
    fixedString = reReplace(fixedString, " [aA-zZ] ", " ")
    fixedString = reReplace(fixedString, "\&", "")
    fixedString = reReplace(fixedString, "\'", " ")
    fixedString = reReplace(fixedString, "\;", " ")
    fixedString = reReplace(fixedString, "\:", " ")
    fixedString = reReplace(fixedString, "\[", " ")
    fixedString = reReplace(fixedString, "\]", " ")
    fixedString = reReplace(fixedString, "\(", " ")
    fixedString = reReplace(fixedString, "\)", " ")
    fixedString = reReplace(fixedString, "\/", " ")
    fixedString = reReplace(fixedString, "\\", " ")
    fixedString = reReplace(fixedString, "\#", " ")
    fixedString = reReplace(fixedString, "\.", "")
    fixedString = reReplace(fixedString, "\?", " ")
    fixedString = reReplace(fixedString, "\-", " ")
    fixedString = reReplace(fixedString, "\_", " ")
    fixedString = reReplace(fixedString, "\%", " ")
    fixedString = reReplace(fixedString, "[0-9]", " ")
    fixedString = reReplace(fixedString, "\$", " ")
    fixedString = reReplace(fixedString, "\|", " ")
    fixedString = reReplace(fixedString, "pct", " ")
    fixedString = reReplace(fixedString, "\s+", " ")
    fixedString = reReplace(fixedString, "\b[a-z]\b", "")
    
 
    #words = fixedString.split()
    #keptWords = []
    #for word in words:
        #if word
        
        #print(words)
    
    fixedString = fixedString.encode(encodingType)
    return(fixedString)


#=================================================================
# We remove some articles with bad headlines
def checkArticle(article):
    headline =  article ['headline']['main']
    if (headline.lower() == "business highlights"):
        isGoodArticle = False
    else:
        isGoodArticle = True
    
    return isGoodArticle
    

#=================================================================
def reReplace(stringToFix, regex, replacmentString):
    value = re.compile(regex)
    replacedString = re.sub(value,replacmentString, stringToFix)
    return replacedString


#=================================================================
# Save the Results to CSV
def saveResults(allArticles, queryTerm, startYear, endYear):
    
    keys = allArticles[0].keys()
    fileTitle = queryTerm + " Articles (" + str(startYear) + "-" + str(endYear) + ").csv"
    with open(fileTitle, "wb") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(allArticles)


## Running Code
allArticles = retrieveArticles(queryTerm, startYear, endYear)
saveResults(allArticles, queryTerm, startYear, endYear)
  