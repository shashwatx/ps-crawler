#!/usr/bin/env python

import coloredlogs
coloredlogs.install()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pdb import set_trace as bp ##for testing
import re
import time
import csv
import os
import logging
logging.basicConfig(filename='execution.log',level=logging.INFO)
logger = logging.getLogger("main")
import click

# prefix for output files
namePrefix='app'

# suffix for output files
nameSuffix='.csv'

# missing suffix in the array
urlSuffix='&showAllReviews=true'

# number of times you need to "scroll-to-end" to see "Show More" button
numBatches=4

# batch report parameter
report_pool_size=5

# skip title if enough reviews found.
reviewLimit=12000

# If we scroll to the exact y of any "Full Review" button,
# we cannot click it as the Navbar's Home button lays on top
# of our button.
# A workaround is to scroll button.y - offset
scrollOffset=100


def obtainOutputFileName(appCounter,s):
    s=re.sub(r"[^\w\s]",'',s)
    s=re.sub(r"[\s+]",'-',s)
    outputFileName=namePrefix+'_'+str(appCounter)+'_'+s+'.csv'
    return outputFileName

def readInputFile(pathToInputFile):
    with open(pathToInputFile) as f:
        text = f.read()
        listOfURLS=text.splitlines()
    return listOfURLS

def getComment(soup):

    # if review is short this is where the content lies
    comment_trimmed=soup.find('span',jsname='bN97Pc').text

    # if review is trimmed, the full content is not put
    # in the expected element.
    # Instead, an element that was previously empty is populated
    # with the full content.
    comment_expanded=soup.find('span',jsname='fbQN7e').text

    # to handle both type of reviews
    comment_to_return=comment_expanded if len(comment_expanded)>0 else comment_trimmed
    return comment_to_return

@click.command()
@click.option('--input', '-i', 'input_', required=True, type=click.Path(exists=True))
@click.option('--output', '-o', required=True, type=click.Path(exists=True))
@click.option('--driver', '-d', 'driver_', required=True, type=click.Path(exists=True))
def run(input_,output,driver_):
    """Simple spider to get Playstore reviews."""

    logger.info('Input: %s.',os.path.expanduser(input_))
    listOfURLS=readInputFile(input_)
    numTitles=len(listOfURLS)
    logger.info('Number of Titles: %d',numTitles)

    logger.info('Web Driver: %s.',os.path.expanduser(driver_))
    chrome_options = Options()
    driver = webdriver.Chrome(executable_path=os.path.realpath(driver_), chrome_options=chrome_options)

    appCounter=-1
    for lt in listOfURLS:
        appCounter=appCounter+1

        link=lt+urlSuffix
        driver.get(link)
        title = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[3]/meta[2]').get_attribute('content')

        outputFile=os.path.join(output,obtainOutputFileName(appCounter,title))

        logger.warn('Title: %s.',title)
        logger.warn('URL: %s', link)
        logger.warn('Output: %s', outputFile)

        flag=0
        iterx=0
        while 1:
            logger.info('App %02d/%02d...Iteration #%d',appCounter,(numTitles-1),iterx)

            if iterx%report_pool_size == 0 and iterx!=0:
                numReviews=len(driver.find_elements_by_xpath("//*[@jsname='fk8dgd']//div[@class='d15Mdf bAhLNe']"))
                logger.info('We are on iteration %d, \t number of reviews: %d',iterx,numReviews)
                if numReviews>reviewLimit:
                    logger.warn('Enough reviews gathered. %d',numReviews)
                    break

            # "Show More" button appears only after 4 complete scroll-to-bottom operations
            for i in range(1,numBatches+1):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.info('Scroll %d is done.', i)
                time.sleep(2)

            # "Show More" should now appear
            try:
                loadMore=driver.find_element_by_xpath("//*[contains(@class,'U26fgb O0WRkf oG5Srb C0oVfc n9lfJ')]").click()
            except Exception , e:
                logger.error('Encountered exception: %s',type(e))
                flag=flag+1
                logger.debug('Flag is now %d.',flag)
                if flag >= 2:
                    logger.warn('I suppose I have reached the end.')
                    logger.debug("Will break")
                    break
                time.sleep(5)
            else:
                flag=0


            iterx=iterx+1


        # find all reviews
        reviews=driver.find_elements_by_xpath("//*[@jsname='fk8dgd']//div[@class='d15Mdf bAhLNe']")

        # find all "Full Review" buttons.
        full_review_buttons=driver.find_elements_by_xpath("//button[@jsname='gxjVle']")
        num_buttons=len(full_review_buttons)
        logger.info('Found %d reviews to expand',num_buttons)


        # scroll to the very top
        logger.info('Will scroll to top.')
        driver.execute_script("window.scrollTo(0, 0);")

        time.sleep(2)

        # click on all "Full Review" buttons
        for idx,btn in enumerate(full_review_buttons):
            logger.info('Expanding review #%d',idx)
            driver.execute_script('window.scrollTo(0, ' + str(btn.location['y']-scrollOffset) + ');')
            btn.click()
            time.sleep(1)

        logger.warn('Finished gathering reviews for title %s',title)
        logger.info('dumping reviews to file...')

        # dump all reviews to file
        with open(outputFile, mode='wb') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["name","ratings","date","helpful vote","comment"])
            for review in reviews:
                try:
                    soup=BeautifulSoup(review.get_attribute("innerHTML"),"lxml")
                    name=soup.find(class_="X43Kjb").text
                    ratings=soup.find('div',role='img').get('aria-label').strip("Rated ")[0]
                    date=soup.find(class_="p2TkOb").text
                    helpful=soup.find(class_="jUL89d y92BAb").text
                    comment=getComment(soup)
                    writer.writerow([name.encode('utf-8'),ratings,date,helpful,comment.encode('utf-8')])

                except Exception , e:
                    logger.error('Encountered exception: %s',str(e))

        logger.warn('All reviews dumped to file %s',outputFile)

if __name__ == "__main__":
    run()

