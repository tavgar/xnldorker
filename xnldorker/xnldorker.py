#!/usr/bin/env python
# Python 3
# xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines
# Full help here: https://github.com/xnl-h4ck3r/xnldorker/blob/main/README.md
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

from ast import arg
import requests
import re
import os
import sys
import argparse
import datetime
from signal import SIGINT, signal
from termcolor import colored
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import tldextract
try:
    from . import __version__
except:
    pass

# Available sources to search
SOURCES = ['duckduckgo','bing','startpage','yahoo', 'google', 'yandex']

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'

# Uer Agents
UA_DESKTOP = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.6; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (X11; Linux i686; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko"
]

# Global variables
args = None
browser = None
stopProgram = False
stopProgramCount = 0
inputDork = ''
duckduckgoEndpoints = set()
bingEndpoints = set()
yahooEndpoints = set()
googleEndpoints = set()
startpageEndpoints = set()
yandexEndpoints = set()
allSubs = set()
sourcesToProcess = []

proxies = []
current_proxy_index = -1

# Functions used when printing messages dependant on verbose options
def verbose():
    return args.verbose or args.vverbose
def vverbose():
    return args.vverbose

def write(text='',pipe=False):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or if the tool has been piped and the pipe parameter is True
    if sys.stdout.isatty() or (not sys.stdout.isatty() and pipe):
        sys.stdout.write(text+'\n')

def writerr(text=''):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or If the tool has been piped to output the send to stderr
    if sys.stdout.isatty():
        sys.stdout.write(text+'\n')
    else:
        sys.stderr.write(text+'\n')

def showVersion():
    try:
        try:
            resp = requests.get('https://raw.githubusercontent.com/xnl-h4ck3r/xnldorker/main/xnldorker/__init__.py',timeout=3)
        except:
            write('Current xnldorker version '+__version__+' (unable to check if latest)\n')
        if __version__ == resp.text.split('=')[1].replace('"','').strip():
            write('Current xnldorker version '+__version__+' ('+colored('latest','green')+')\n')
        else:
            write('Current xnldorker version '+__version__+' ('+colored('outdated','red')+')\n')
    except:
        pass
      
def showBanner():
    writerr('')
    writerr(colored(r'            _     _            _', 'red'))
    writerr(colored(r'__  ___ __ | | __| | ___  _ __| | _____ _ __', 'yellow'))
    writerr(colored(r"\ \/ / '_ \| |/ _` |/ _ \| '__| |/ / _ \ '__|", 'green'))
    writerr(colored(r' >  <| | | | | (_| | (_) | |  |   <  __/ |', 'cyan'))
    writerr(colored(r'/_/\_\_| |_|_|\__,_|\___/|_|  |_|\_\___|_|', 'magenta'))
    writerr(colored('                             by Xnl-h4ck3r','white'))
    writerr('')
    showVersion()

def handler(signal_received, frame):
    """
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    """
    global stopProgram, stopProgramCount

    if stopProgram:
        stopProgramCount = stopProgramCount + 1
        if stopProgramCount == 1:
            writerr(colored('>>> Please be patient... Trying to save data and end gracefully!','red'))
        elif stopProgramCount == 2:
            writerr(colored('>>> SERIOUSLY... YOU DON\'T WANT YOUR DATA SAVED?!','red'))
        elif stopProgramCount == 3:
            writerr(colored('>>> Patience isn\'t your strong suit eh? ¯\_(ツ)_/¯','red'))
            sys.exit()
    else:
        stopProgram = True
        writerr(colored('>>> "Oh my God, they killed Kenny... and xnldorker!" - Kyle',"red"))
        writerr(colored('>>> Attempting to rescue any data gathered so far...', "red"))

def getSubdomain(url):
    try:
        # Just get the hostname of the url 
        tldExtract = tldextract.extract(url)
        return tldExtract.subdomain
    except Exception as e:
        writerr(colored('ERROR getSubdomain 1: ' + str(e), 'red')) 

async def wait_for_word_or_sleep(word, timeout):
    """
    Called when an antibot screen is detected on a source. It will resume again when the timeout is reached, or if the passed word is typed and ENTER pressed
    """
    loop = asyncio.get_event_loop()
    word_entered = asyncio.Event()

    def on_input_received():
        input_text = sys.stdin.readline().strip()
        if input_text == word:
            word_entered.set()

    loop.add_reader(sys.stdin.fileno(), on_input_received)

    try:
        await asyncio.wait_for(word_entered.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass  # Timeout reached, continue with the script
    finally:
        loop.remove_reader(sys.stdin.fileno())
              
async def getResultsDuckDuckGo(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        div_content = soup.find('div', id='web_content_wrapper')
        if div_content:
            a_tags = div_content.find_all('a')
            for a in a_tags:
                href = a.get('href')
                if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*duckduckgo\.[^\/\.]{2,}', href):
                    endpoints.append(href.strip())
                    # If the same search is going to be resubmitted without subs, get the subdomain
                    if args.resubmit_without_subs:
                        allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR getResultsDuckDuckGo 1: ' + str(e), 'red')) 
        
async def getDuckDuckGo(browser, dork, semaphore):
    global stopProgram
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ DuckDuckGo ] Starting...', 'green'))
        
        # Call with parameters:
        #  kc=-1 - Don't auto load images
        await page.goto(f'https://duckduckgo.com/?kc=-1&ia=web&q={dork}', timeout=args.timeout*1000)
        pageNo = 1
        
        # If captcha is shown then allow time to submit it
        captcha = await page.query_selector('#anomaly-modal__modal.anomaly-modal__modal')
        if captcha:
            if args.show_browser:
                writerr(colored(f'[ DuckDuckGo ] reCAPTCHA needs responding to. Process will resume in {arg.antibot_timeout} seconds, or when you type "duckduckgo" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("duckduckgo", args.antibot_timeout)
                writerr(colored(f'[ DuckDuckGo ] Resuming...', 'green'))
            else:
                writerr(colored('[ DuckDuckGo ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)
        
        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass

        captcha = await page.query_selector('#anomaly-modal__modal.anomaly-modal__modal')
        if captcha:
            writerr(colored('[ DuckDuckGo ] Failed to complete reCAPTCHA','red'))
            return set(endpoints)
               
        # Function to check if the button is disabled and enable it if necessary
        async def enable_more_results():
            more_results_button = await page.query_selector('#more-results')
            if more_results_button:
                is_disabled = await more_results_button.evaluate('(element) => element.disabled')
                if is_disabled:
                    await page.evaluate('(element) => element.disabled = false', more_results_button)

        # Function to check for the presence of the button and click it if available
        async def click_more_results():
            if await page.query_selector('#more-results'):
                await page.click('#more-results')
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)

        # Loop to repeatedly check for the button and click it until it doesn't exist
        while await page.query_selector('#more-results'):
            if stopProgram:
                break
            await enable_more_results()
            if vverbose():
                pageNo += 1
                writerr(colored('[ DuckDuckGo ] Clicking "More Results" button to display page '+str(pageNo), 'green', attrs=['dark'])) 
            await click_more_results()
            # Get the results so far, just in case it ends early
            endpoints =  await getResultsDuckDuckGo(page, endpoints)

        # Get all the results
        endpoints = await getResultsDuckDuckGo(page, endpoints)
        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ DuckDuckGo ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
     
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ DuckDuckGo ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ DuckDuckGo ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ DuckDuckGo ] ERROR getDuckDuckGo 1: ' + str(e), 'red'))  
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('DuckDuckGo',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
def extractBingEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        div_content = soup.find('div', id='b_content')
        if div_content:
            a_tags = div_content.find_all('a')
            for a in a_tags:
                href = a.get('href')
                recommendations = a.find_parent('div', class_='pageRecoContainer')
                if href and href.startswith('http') and not recommendations and not re.match(r'^https?:\/\/([\w-]+\.)*bing\.[^\/\.]{2,}', href) and not re.match(r'^https?:\/\/go\.microsoft\.com', href):
                    endpoints.append(href.strip())
                    # If the same search is going to be resubmitted without subs, get the subdomain
                    if args.resubmit_without_subs:
                        allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractBingEndpoints 1: ' + str(e), 'red')) 
        
async def getBing(browser, dork, semaphore):
    try:
        endpoints = [] 
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Bing ] Starting...', 'green'))
            
        await page.goto(f'https://www.bing.com/search?q={dork}', timeout=args.timeout*1000)

        # Check if the cookie banner exists and click reject if it does
        if await page.query_selector('#bnp_btn_reject'):
            # Click the button to reject
            await page.click('#bnp_btn_reject')
            
        # Collect endpoints from the initial page
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        pageNo = 1
        endpoints = extractBingEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        while True:
            if stopProgram:
                break
            # Find the link with the title "Next page"
            if await page.query_selector('a[title="Next page"]'):
                await page.click('a[title="Next page"]')
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                pageNo += 1
                if vverbose():
                    writerr(colored('[ Bing ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
                
                # Collect endpoints from the current page
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                endpoints += extractBingEndpoints(soup)
            else:
                # No "Next page" link found, exit the loop
                break

        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Bing ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Bing ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Bing ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Bing ] ERROR getBing 1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Bing',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
def extractStartpageEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        result_links = soup.find_all('a', class_=re.compile('.*result-link.*'))
        for link in result_links:
            href = link.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*startpage\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractStartpageEndpoints 1: ' + str(e), 'red')) 
        
async def getStartpage(browser, dork, semaphore):
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Startpage ] Starting...', 'green'))
            
        await page.goto(f'https://www.startpage.com/', timeout=args.timeout*1000)
        
        # Wait for the search results to be fully loaded
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        # Check if bot detection is shown
        if '/sp/captcha' in page.url:
            if args.show_browser:
                writerr(colored(f'[ Startpage ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "startpage" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("startpage", args.antibot_timeout)
                writerr(colored(f'[ Startpage ] Resuming...', 'green'))
            else:
                writerr(colored('[ Startpage ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)

        try:
            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        except:
            pass

        # Check if bot detection is still shown
        if '/sp/captcha' in page.url:
            writerr(colored('[ Startpage ] Failed to complete CAPTCHA','red'))
            return set(endpoints)
        
        await page.fill('input[title="Search"]', dork)
        await page.click('button.search-btn')
        
        # Wait for the search results to be fully loaded
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        # Check if any '.result-link' exists
        try:
            await page.wait_for_selector('.result-link', timeout=1000)  # Short timeout to check existence
        except:
            if verbose():
                writerr(colored('[ Startpage ] Complete! - 0 endpoints found', 'green')) 
            await page.close()
            return set() 
        
        # Collect endpoints from the initial page
        if vverbose():
            writerr(colored('[ Startpage ] Getting endpoints from page 1', 'green', attrs=['dark'])) 
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        pageNo = 1
        endpoints = extractStartpageEndpoints(soup)

        # Loop until there is no submit button in the last form with action="/sp/search"
        while True:
            if stopProgram:
                break
            # Check if bot detection is shown
            if '/sp/captcha' in page.url:
                if args.show_browser:
                    writerr(colored(f'[ Startpage ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "startpage" and press ENTER...','yellow')) 
                    await wait_for_word_or_sleep("startpage", args.antibot_timeout)
                    writerr(colored(f'[ Startpage ] Resuming...', 'green'))
                else:
                    writerr(colored('[ Startpage ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                    return set(endpoints)
            
            try:
                # Wait for the search results to be fully loaded and have links
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
            except:
                pass

            # Check if bot detection is still shown
            if '/sp/captcha' in page.url:
                writerr(colored('[ Startpage ] Failed to complete CAPTCHA','red'))
                return set(endpoints)
        
            # Locate all forms with action="/sp/search" on the page
            forms = await page.query_selector_all('form[action="/sp/search"]')
            last_form = forms[-1]  # Get the last form
            
            # Get the current value of the "page" input field
            try:
                curr_page_value = await last_form.evaluate('(form) => form.querySelector("input[name=\'page\']").value')
            except:
                curr_page_value = 1
            
            # If the current "page" value has not increased, break out of the loop
            if pageNo == curr_page_value:
                break
            
            # Click the submit button for the last form
            await last_form.click()

            # Wait for the search results to be fully loaded and have links
            await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)

            # Check if any '.result-link' exists
            try:
                await page.wait_for_selector('.result-link', timeout=1000)  # Short timeout to check existence
            except:
                break  # Break the loop if no '.result-link' found
        
            if vverbose():
                writerr(colored('[ Startpage ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
            
            # Collect endpoints from the current page
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            endpoints += extractStartpageEndpoints(soup)

            # Update the previous "page" value
            pageNo = curr_page_value

        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Startpage ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Startpage ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Startpage ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Startpage ] ERROR getStartpage1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Startpage',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
def extractYahooEndpoints(soup):
    global allSubs
    try:
        endpoints = []
        div_content = soup.find('div', id='results')
        if div_content:
            a_tags = div_content.find_all('a')
            for a in a_tags:
                # Don't add links from Ads
                if not a.find_parent(class_="searchCenterTopAds") and not a.find_parent(class_="searchCenterBottomAds"):
                    href = a.get('href')
                    if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*yahoo\.[^\/\.]{2,}', href) and not re.match(r'^https?:\/\/([\w-]+\.)*bingj\.com', href):
                        endpoints.append(href.strip())
                        # If the same search is going to be resubmitted without subs, get the subdomain
                        if args.resubmit_without_subs:
                            allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR extractYahooEndpoints 1: ' + str(e), 'red')) 
        
def extractYahooResultNumber(url):
    try:
        match = re.search(r'\b(?:b=)([^&]+)', url)
        if match:
            return match.group(1)
        return 0
    except Exception as e:
        writerr(colored('ERROR extractYahooResultNumber 1: ' + str(e), 'red')) 
        
async def getYahoo(browser, dork, semaphore):
    try:
        endpoints = []
        page = None
        await semaphore.acquire()
        page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
        
        if verbose():
            writerr(colored('[ Yahoo ] Starting...', 'green'))
        
        await page.goto(f'https://www.yahoo.com/search?q={dork}', timeout=args.timeout*1000)

        # Check if the cookie banner exists and click "Go to end" and then "Agree" if it does
        cookie = await page.query_selector('#scroll-down-btn')
        if cookie:
            await cookie.click()
        cookieAgree = await page.query_selector('button[name="agree"][value="agree"]')
        if cookieAgree:
            await cookieAgree.click()
        
        # Submit the search form
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        await page.wait_for_selector("form")
        await page.press("form", "Enter")
        await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
        
        # Collect endpoints from the initial page
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        endpoints = extractYahooEndpoints(soup)

        # Main loop to keep navigating to next pages until there's no "Next page" link
        pageNo = 1
        oldResultNumber = 1
        while True:
            if stopProgram:
                break
            # Find the link with the title "Next page"
            next_page_link = await page.query_selector('a.next')
            if next_page_link:
                # Extract Result number value from the URL of the current page
                pageUrl = page.url
                nextResultNumber = extractYahooResultNumber(pageUrl)
                # If it is the same as the last page, exit the loop
                if nextResultNumber == oldResultNumber:
                    break
                oldResultNumber = nextResultNumber
                
                await next_page_link.click()
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                pageNo += 1
                if vverbose():
                    writerr(colored('[ Yahoo ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
                
                # Collect endpoints from the current page
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                endpoints += extractYahooEndpoints(soup)
                
            else:
                # No "Next page" link found, exit the loop
                break
        
        await page.close()

        setEndpoints = set(endpoints)
        if verbose():
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Yahoo ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Yahoo ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Yahoo ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
        else:
            writerr(colored('[ Yahoo ] ERROR getYahoo1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the page
        if args.debug and page is not None:
            await savePageContents('Yahoo',page)
        return set(endpoints)
    finally:
        try:
            await page.close()
            semaphore.release()
        except:
            pass
        
async def getResultsGoogle(page, endpoints):
    global allSubs
    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        a_tags = soup.find_all('a')
        for a in a_tags:
            href = a.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*google\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:
                    allSubs.add(getSubdomain(href.strip()))
        return endpoints
    except Exception as e:
        writerr(colored('ERROR getResultsGoogle 1: ' + str(e), 'red')) 
        
async def getGoogle(browser, dork, semaphore):
    global stopProgram
    tried_proxies = set()
    proxies_available = len(proxies) > 0
    max_proxy_retries = len(proxies) if proxies_available else 0
    proxy_retries = 0
    
    try:
        endpoints = []
        page = None
        context = None
        await semaphore.acquire()
        
        while proxy_retries <= max_proxy_retries:
            current_proxy = None
            
            try:
                # Clean up previous context and page if they exist
                if page:
                    await page.close()
                if context:
                    await context.close()
                
                # Create a new context with the current proxy if available
                if proxies_available:
                    current_proxy = get_next_proxy()
                    if current_proxy in tried_proxies and len(tried_proxies) >= len(proxies):
                        # We've tried all proxies
                        writerr(colored('[ Google ] All proxies have been tried and failed with CAPTCHA', 'red'))
                        return set(endpoints)
                    
                    tried_proxies.add(current_proxy)
                    proxy_retries += 1
                    
                    if verbose():
                        writerr(colored(f'[ Google ] Using proxy: {current_proxy}', 'green'))
                    
                    context = await browser.new_context(ins compatibility with all proxy types
                        proxy={"server": current_proxy},
                        user_agent=DEFAULT_USER_AGENTy},
                    )   user_agent=DEFAULT_USER_AGENT
                    page = await context.new_page()
                else:age = await context.new_page()
                    page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
                    page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
                if verbose():
                    writerr(colored('[ Google ] Starting...', 'green'))
                    writerr(colored('[ Google ] Starting...', 'green'))
                # Use the parameters:
                #  tbs=li:1 - Verbatim search
                #  hl=en - English languagech
                #  filter=0 - Show near duplicate content
                #  num=100 - Show upto 100 results per page
                extended_timeout = args.timeout * 3 if proxies_available else args.timeout
                await page.goto(f'https://www.google.com/search?tbs=li:1&hl=en&filter=0&num=100&q={dork}', 
                               timeout=extended_timeout*1000)ch?tbs=li:1&hl=en&filter=0&num=100&q={dork}', 
                               timeout=extended_timeout*1000)
                # Increased timeout for network idle when using proxies
                await page.wait_for_load_state('domcontentloaded', timeout=extended_timeout*1000)
                await page.wait_for_load_state('domcontentloaded', timeout=extended_timeout*1000)
                pageNo = 1
                pageNo = 1
                # If captcha is shown then try next proxy or allow time to submit it
                captcha = await page.query_selector('form#captcha-form')to submit it
                if captcha:wait page.query_selector('form#captcha-form')
                    if proxies_available:
                        writerr(colored(f'[ Google ] reCAPTCHA detected with proxy {current_proxy}, trying next proxy...', 'yellow'))
                        continuecolored(f'[ Google ] reCAPTCHA detected with proxy {current_proxy}, trying next proxy...', 'yellow'))
                    elif args.show_browser:
                        writerr(colored(f'[ Google ] reCAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "google" and press ENTER...','yellow')) 
                        await wait_for_word_or_sleep("google", args.antibot_timeout)Process will resume in {args.antibot_timeout} seconds, or when you type "google" and press ENTER...','yellow')) 
                        writerr(colored(f'[ Google ] Resuming...', 'green'))timeout)
                    else:riterr(colored(f'[ Google ] Resuming...', 'green'))
                        writerr(colored('[ Google ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser or --proxy-list','red'))
                        return set(endpoints)ogle ] reCAPTCHA needed responding to. Consider using option -sb / --show-browser or --proxy-list','red'))
                        return set(endpoints)
                try:
                    # Wait for the search results to be fully loaded and have links
                    await page.wait_for_load_state('networkidle', timeout=extended_timeout*1000)
                except:it page.wait_for_load_state('networkidle', timeout=extended_timeout*1000)
                    # If timeout occurs, try to continue anyway as we might have partial results
                    if verbose():occurs, try to continue anyway as we might have partial results
                        writerr(colored('[ Google ] Network idle timeout - continuing with available results', 'yellow'))
                        writerr(colored('[ Google ] Network idle timeout - continuing with available results', 'yellow'))
                # Check if bot detection is still shown
                captcha = await page.query_selector('form#captcha-form')
                if captcha:wait page.query_selector('form#captcha-form')
                    if proxies_available:
                        writerr(colored(f'[ Google ] reCAPTCHA still present with proxy {current_proxy}, trying next proxy...', 'yellow'))
                        continuecolored(f'[ Google ] reCAPTCHA still present with proxy {current_proxy}, trying next proxy...', 'yellow'))
                    else:ontinue
                        writerr(colored('[ Google ] Failed to complete reCAPTCHA','red'))
                        return set(endpoints)ogle ] Failed to complete reCAPTCHA','red'))
                        return set(endpoints)
                # If the cookies notice is shown, accept it
                cookieAccept = await page.query_selector('button:has-text("Accept all")')
                if cookieAccept:wait page.query_selector('button:has-text("Accept all")')
                    await cookieAccept.click()
                    await cookieAccept.click()
                # If the dialog box asking if you want location specific search, say Not now
                locationSpecific = await page.query_selector('g-raised-button:has-text("Not now")')
                if locationSpecific:wait page.query_selector('g-raised-button:has-text("Not now")')
                    await locationSpecific.click()
                    await locationSpecific.click()
                # Collect endpoints from the initial page
                endpoints = await getResultsGoogle(page, endpoints)
                endpoints = await getResultsGoogle(page, endpoints)
                # Main loop to keep navigating to next pages until there's no "Next page" link
                while True: to keep navigating to next pages until there's no "Next page" link
                    if stopProgram:
                        breakogram:
                    # Get href from the Next button
                    next_button = await page.query_selector('#pnnext')
                    if next_button:wait page.query_selector('#pnnext')
                        next_href = await next_button.get_attribute('href')
                        if next_href:wait next_button.get_attribute('href')
                            next_url = 'https://www.google.com' + next_href
                            await page.goto(next_url, timeout=extended_timeout * 1000)
                            await page.wait_for_load_state('domcontentloaded', timeout=extended_timeout * 1000)
                            await page.wait_for_load_state('domcontentloaded', timeout=extended_timeout * 1000)
                            pageNo += 1
                            if vverbose():
                                writerr(colored('[ Google ] Getting endpoints from page ' + str(pageNo), 'green', attrs=['dark']))
                                writerr(colored('[ Google ] Getting endpoints from page ' + str(pageNo), 'green', attrs=['dark']))
                            # Collect endpoints from the current page
                            endpoints += await getResultsGoogle(page, endpoints)
                    else:   endpoints += await getResultsGoogle(page, endpoints)
                        # No "Next" button found, exit the loop
                        break"Next" button found, exit the loop
                        break
                # Successfully completed search - break out of the retry loop
                breakcessfully completed search - break out of the retry loop
                break
            except Exception as e:
                if current_proxy::
                    if 'net::ERR_PROXY_CONNECTION_FAILED' in str(e):
                        writerr(colored(f'[ Google ] Proxy connection failed: {current_proxy}', 'red'))
                    elif 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):current_proxy}', 'red'))
                        writerr(colored(f'[ Google ] Proxy timed out: {current_proxy}', 'red'))
                    elif 'net::ERR_ABORTED' in str(e):roxy timed out: {current_proxy}', 'red'))
                        writerr(colored(f'[ Google ] Request aborted with proxy: {current_proxy}', 'red'))
                    else:riterr(colored(f'[ Google ] Request aborted with proxy: {current_proxy}', 'red'))
                        writerr(colored(f'[ Google ] Error with proxy {current_proxy}: {str(e)}', 'red'))
                        writerr(colored(f'[ Google ] Error with proxy {current_proxy}: {str(e)}', 'red'))
                    # Only continue if we haven't tried all proxies yet
                    if proxies_available and len(tried_proxies) < len(proxies):
                        continuevailable and len(tried_proxies) < len(proxies):
                    else:ontinue
                        raise e
                else:   raise e
                    # Re-raise the exception to be caught by the outer try/except
                    raise eise the exception to be caught by the outer try/except
                    raise e
        setEndpoints = set(endpoints)
        if verbose():= set(endpoints)
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Google ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints(f'[ Google ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Google ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Google ] Search aborted - got {str(noOfEndpoints)} results', 'red')) (e):
        else:riterr(colored(f'[ Google ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
            writerr(colored('[ Google ] ERROR getGoogle1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the pagegle1: ' + str(e), 'red')) 
        if args.debug and page is not None: the page
            await savePageContents('Google',page)
        return set(endpoints)tents('Google',page)
    finally:rn set(endpoints)
        try:
            if page:
                await page.close()
            if context:age.close()
                await context.close()
            semaphore.release()lose()
        except:aphore.release()
            pass
            pass
def extractYandexEndpoints(soup):
    global allSubsndpoints(soup):
    try:al allSubs
        endpoints = []
        result_links = soup.find_all('a', class_=re.compile('.*organic__url.*'))
        for link in result_links:all('a', class_=re.compile('.*organic__url.*'))
            href = link.get('href')
            if href and href.startswith('http') and not re.match(r'^https?:\/\/([\w-]+\.)*yandex\.[^\/\.]{2,}', href):
                endpoints.append(href.strip())) and not re.match(r'^https?:\/\/([\w-]+\.)*yandex\.[^\/\.]{2,}', href):
                # If the same search is going to be resubmitted without subs, get the subdomain
                if args.resubmit_without_subs:to be resubmitted without subs, get the subdomain
                    allSubs.add(getSubdomain(href.strip()))
        return endpointsubs.add(getSubdomain(href.strip()))
    except Exception as e:
        writerr(colored('ERROR extractYandexEndpoints 1: ' + str(e), 'red')) 
        writerr(colored('ERROR extractYandexEndpoints 1: ' + str(e), 'red')) 
async def getYandex(browser, dork, semaphore):
    try:f getYandex(browser, dork, semaphore):
        endpoints = []
        page = None []
        await semaphore.acquire()
        # Set the gdpr cookie to reduce the chances of getting Captcha page a bit
        context = await browser.new_context(chances of getting Captcha page a bit
            storage_state={wser.new_context(
                'cookies': [{
                    'name': 'gdpr',
                    'value': '0',',
                    'domain': '.yandex.com',
                    'path': '/'.yandex.com',
                }]  'path': '/'
            }   }]
        )   }
        page = await context.new_page()
        page = await context.new_page()
        if verbose():
            writerr(colored('[ Yandex ] Starting...', 'green'))
            writerr(colored('[ Yandex ] Starting...', 'green'))
        await page.goto(f'https://yandex.com/search/?text={dork}', timeout=args.timeout*1000)
        await page.goto(f'https://yandex.com/search/?text={dork}', timeout=args.timeout*1000)
        # Check if bot detection is shown
        if '/showcaptcha' in page.url:own
            if args.show_browser:.url:
                writerr(colored(f'[ Yandex ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...','yellow')) 
                await wait_for_word_or_sleep("yandex", args.antibot_timeout)ocess will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...','yellow')) 
                writerr(colored(f'[ Yandex ] Resuming...', 'green'))timeout)
            else:riterr(colored(f'[ Yandex ] Resuming...', 'green'))
                writerr(colored('[ Yandex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                return set(endpoints)ndex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
        try:    return set(endpoints)
            await page.wait_for_load_state('networkidle', timeout=1000)
        except:it page.wait_for_load_state('networkidle', timeout=1000)
            pass
            pass
        # If still on Captcha page, then exit
        if '/showcaptcha' in page.url:en exit
            writerr(colored('[ Yandex ] Failed to complete CAPTCHA','red'))
            return set(endpoints)ndex ] Failed to complete CAPTCHA','red'))
            return set(endpoints)
        # Collect endpoints from the initial page
        if vverbose():oints from the initial page
            writerr(colored('[ Yandex ] Getting endpoints from page 1', 'green', attrs=['dark'])) 
        content = await page.content()] Getting endpoints from page 1', 'green', attrs=['dark'])) 
        soup = BeautifulSoup(content, 'html.parser')
        pageNo = 1utifulSoup(content, 'html.parser')
        endpoints = extractYandexEndpoints(soup)
        endpoints = extractYandexEndpoints(soup)
        # Loop until there is no submit button in the last form with action="/sp/search"
        while True:l there is no submit button in the last form with action="/sp/search"
            if stopProgram:
                breakogram:
                break
            # Click the Next button
            await page.click('a[aria-label="Next page"]')
            pageNo += 1click('a[aria-label="Next page"]')
            pageNo += 1
            # Check if bot detection is shown
            if '/showcaptcha' in page.url:own
                if args.show_browser:.url:
                    writerr(colored(f'[ Yandex ] CAPTCHA needs responding to. Process will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...','yellow')) 
                    await wait_for_word_or_sleep("yandex", args.antibot_timeout)ocess will resume in {args.antibot_timeout} seconds, or when you type "yandex" and press ENTER...','yellow')) 
                    writerr(colored(f'[ Yandex ] Resuming...', 'green'))timeout)
                else:riterr(colored(f'[ Yandex ] Resuming...', 'green'))
                    writerr(colored('[ Yandex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                    return set(endpoints)ndex ] CAPTCHA needed responding to. Consider using option -sb / --show-browser','red'))
                    return set(endpoints)
            try:
                # Wait for the search results to be fully loaded and have links
                await page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
            except:it page.wait_for_load_state('networkidle', timeout=args.timeout*1000)
                pass
                pass
            # If still on Captcha page, then exit
            if '/showcaptcha' in page.url:en exit
                writerr(colored('[ Yandex ] Failed to complete CAPTCHA','red'))
                return set(endpoints)ndex ] Failed to complete CAPTCHA','red'))
                return set(endpoints)
            # Check if any classes containing organic__url exist
            try:eck if any classes containing organic__url exist
                await page.wait_for_selector('.organic__url', timeout=1000)
            except:it page.wait_for_selector('.organic__url', timeout=1000)
                break  # Break the loop if no '.organic__url' found
                break  # Break the loop if no '.organic__url' found
            if vverbose():
                writerr(colored('[ Yandex ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
                writerr(colored('[ Yandex ] Getting endpoints from page '+str(pageNo), 'green', attrs=['dark'])) 
            # Collect endpoints from the current page
            content = await page.content()urrent page
            soup = BeautifulSoup(content, 'html.parser')
            endpoints += extractYandexEndpoints(soup)r')
            endpoints += extractYandexEndpoints(soup)
        await page.close()
        await page.close()
        setEndpoints = set(endpoints)
        if verbose():= set(endpoints)
            noOfEndpoints = len(setEndpoints)
            writerr(colored(f'[ Yandex ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints(f'[ Yandex ] Complete! {str(noOfEndpoints)} endpoints found', 'green')) 
        return setEndpoints
    except Exception as e:
        noOfEndpoints  = len(set(endpoints))
        if 'net::ERR_TIMED_OUT' in str(e) or 'Timeout' in str(e):
            writerr(colored(f'[ Yandex ] Page timed out - got {str(noOfEndpoints)} results', 'red'))
        elif 'net::ERR_ABORTED' in str(e) or 'Target page, context or browser has been closed' in str(e):
            writerr(colored(f'[ Yandex ] Search aborted - got {str(noOfEndpoints)} results', 'red')) (e):
        else:riterr(colored(f'[ Yandex ] Search aborted - got {str(noOfEndpoints)} results', 'red')) 
            writerr(colored('[ Yandex ] ERROR getYandex1: ' + str(e), 'red')) 
        # If debug mode then save a copy of the pagedex1: ' + str(e), 'red')) 
        if args.debug and page is not None: the page
            await savePageContents('Yandex',page)
        return set(endpoints)tents('Yandex',page)
    finally:rn set(endpoints)
        try:
            await page.close()
            semaphore.release()
        except:aphore.release()
            pass
            pass
async def savePageContents(source, page):
    try:f savePageContents(source, page):
        # Press the "Escape" key to stop page loading
        await page.keyboard.press("Escape")ge loading
        await page.keyboard.press("Escape")
        # Wait for a short duration to ensure the page loading is stopped
        await asyncio.sleep(2000)on to ensure the page loading is stopped
        await asyncio.sleep(2000)
        # Get the page contents and save to file
        content = await page.content()ve to file
        if content != '' and content != '<html><head></head><body></body></html>':
            now = datetime.datetime.now()<html><head></head><body></body></html>':
            timestamp = now.strftime("%Y%m%d-%H%M%S")
            filename = f"xnldorker_{source}_{timestamp}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content), encoding="utf-8") as file:
            writerr(colored(f'[ {source} ] Saved HTML content to {filename}', 'cyan')) 
    except Exception as e:d(f'[ {source} ] Saved HTML content to {filename}', 'cyan')) 
        writerr(colored(f'[ {source} ] Unable to save page contents: {str(e)}', 'cyan')) 
        writerr(colored(f'[ {source} ] Unable to save page contents: {str(e)}', 'cyan')) 
async def processInput(dork):
    global browser, sourcesToProcess, duckduckgoEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, yandexEndpoints
    try:al browser, sourcesToProcess, duckduckgoEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, yandexEndpoints
        
        # Create a single browser instance
        async with async_playwright() as p:
            if args.show_browser:ht() as p:
                browser = await p.chromium.launch(headless=False)
            else:rowser = await p.chromium.launch(headless=False)
                browser = await p.chromium.launch()
                browser = await p.chromium.launch()
            # Define a dictionary to hold the results for each source
            resultsDict = {}onary to hold the results for each source
            resultsDict = {}
            # Define a semaphore to limit concurrent tasks. This is determined by the -cs / --concurrent-sources argument
            concurrentSources = args.concurrent_sourcessks. This is determined by the -cs / --concurrent-sources argument
            if concurrentSources == 0 or concurrentSources > len(sourcesToProcess):
                concurrentSources = len(sourcesToProcess)s > len(sourcesToProcess):
            semaphore = asyncio.Semaphore(concurrentSources)
            semaphore = asyncio.Semaphore(concurrentSources)
            # Define a list to hold the sources included in the gather call
            includedSources = []old the sources included in the gather call
            includedSources = []
            # Check and add coroutines for any required sources
            try:eck and add coroutines for any required sources
                if 'duckduckgo' in sourcesToProcess:
                    includedSources.append(getDuckDuckGo(browser, dork, semaphore))
                if 'bing' in sourcesToProcess:DuckDuckGo(browser, dork, semaphore))
                    includedSources.append(getBing(browser, dork, semaphore))
                if 'startpage' in sourcesToProcess:browser, dork, semaphore))
                    includedSources.append(getStartpage(browser, dork, semaphore))
                if 'yahoo' in sourcesToProcess:tartpage(browser, dork, semaphore))
                    includedSources.append(getYahoo(browser, dork, semaphore))
                if 'google' in sourcesToProcess:hoo(browser, dork, semaphore))
                    includedSources.append(getGoogle(browser, dork, semaphore))
                if 'yandex' in sourcesToProcess:ogle(browser, dork, semaphore))
                    includedSources.append(getYandex(browser, dork, semaphore))
            except: includedSources.append(getYandex(browser, dork, semaphore))
                pass
                pass
            # Run all searches concurrently using the same browser instance
            results = await asyncio.gather(*includedSources)rowser instance
            results = await asyncio.gather(*includedSources)
            # Populate the results dictionary and endpoint lists
            for source, result in zip(sourcesToProcess, results):
                if source not in resultsDict:  # Check if the source is not already in the resultsDict
                    resultsDict[source] = result  # If not, add itce is not already in the resultsDict
                else:esultsDict[source] = result  # If not, add it
                    # If the source is already in the resultsDict, append new data to existing data
                    resultsDict[source].update(result)resultsDict, append new data to existing data
                    resultsDict[source].update(result)
                # Update the endpoint lists as well
                if source == 'duckduckgo':s as well
                    duckduckgoEndpoints.update(result)
                elif source == 'bing':s.update(result)
                    bingEndpoints.update(result)
                elif source == 'startpage':sult)
                    startpageEndpoints.update(result)
                elif source == 'yahoo':update(result)
                    yahooEndpoints.update(result)
                elif source == 'google':e(result)
                    googleEndpoints.update(result)
                elif source == 'yandex':te(result)
                    yandexEndpoints.update(result)
                    yandexEndpoints.update(result)
            # Close the browser instance once all searches are done
            try:ose the browser instance once all searches are done
                await browser.close()
            except:it browser.close()
                pass
                pass
    except Exception as e:
        writerr(colored('ERROR processInput 1: ' + str(e), 'red')) 
    finally:err(colored('ERROR processInput 1: ' + str(e), 'red')) 
        try:
            await browser.close()
        except:it browser.close()
            pass
            pass
async def processOutput():
    global duckduckgoEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, yandexEndpoints, sourcesToProcess
    try:al duckduckgoEndpoints, bingEndpoints, startpageEndpoints, yahooEndpoints, googleEndpoints, yandexEndpoints, sourcesToProcess
        allEndpoints = set()
        allEndpoints = set()
        # If --output-sources was passed, then keep the source in the endpoint, otherwise we need a unique set without source
        if args.output_sources:as passed, then keep the source in the endpoint, otherwise we need a unique set without source
            if duckduckgoEndpoints:
                allEndpoints.update(f'[ DuckDuckGo ] {endpoint}' for endpoint in duckduckgoEndpoints)
            if bingEndpoints:update(f'[ DuckDuckGo ] {endpoint}' for endpoint in duckduckgoEndpoints)
                allEndpoints.update(f'[ Bing ] {endpoint}' for endpoint in bingEndpoints)
            if startpageEndpoints:e(f'[ Bing ] {endpoint}' for endpoint in bingEndpoints)
                allEndpoints.update(f'[ StartPage ] {endpoint}' for endpoint in startpageEndpoints)
            if yahooEndpoints:pdate(f'[ StartPage ] {endpoint}' for endpoint in startpageEndpoints)
                allEndpoints.update(f'[ Yahoo ] {endpoint}' for endpoint in yahooEndpoints)
            if googleEndpoints:date(f'[ Yahoo ] {endpoint}' for endpoint in yahooEndpoints)
                allEndpoints.update(f'[ Google ] {endpoint}' for endpoint in googleEndpoints)
            if yandexEndpoints:date(f'[ Google ] {endpoint}' for endpoint in googleEndpoints)
                allEndpoints.update(f'[ Yandex ] {endpoint}' for endpoint in yandexEndpoints)
        else:   allEndpoints.update(f'[ Yandex ] {endpoint}' for endpoint in yandexEndpoints)
            if duckduckgoEndpoints:
                allEndpoints |= duckduckgoEndpoints
            if bingEndpoints:|= duckduckgoEndpoints
                allEndpoints |= bingEndpoints
            if startpageEndpoints:ngEndpoints
                allEndpoints |= startpageEndpoints
            if yahooEndpoints:= startpageEndpoints
                allEndpoints |= yahooEndpoints
            if googleEndpoints: yahooEndpoints
                allEndpoints |= googleEndpoints
            if yandexEndpoints: googleEndpoints
                allEndpoints |= yandexEndpoints
                allEndpoints |= yandexEndpoints
        if verbose() and sys.stdin.isatty():
            writerr(colored('\nTotal endpoints found: '+str(len(allEndpoints))+' 🤘  ', 'cyan')+str(sourcesToProcess))
            writerr(colored('\nTotal endpoints found: '+str(len(allEndpoints))+' 🤘  ', 'cyan')+str(sourcesToProcess))
        # If the -ow / --output_overwrite argument was passed and the file exists already, get the contents of the file to include
        appendedResults = False_overwrite argument was passed and the file exists already, get the contents of the file to include
        if args.output and not args.output_overwrite:
            try:output and not args.output_overwrite:
                existingEndpoints = open(os.path.expanduser(args.output), "r")
                appendedResults = Trueen(os.path.expanduser(args.output), "r")
                for endpoint in existingEndpoints.readlines():
                    allEndpoints.add(endpoint.strip())lines():
            except: allEndpoints.add(endpoint.strip())
                pass
                pass
        # If an output file was specified, open it
        if args.output is not None:cified, open it
            try:output is not None:
                # If the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
                try: the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
                    f = os.path.basename(args.output)
                    p = args.output[:-(len(f))-1]put)
                    if p != "" and not os.path.exists(p):
                        os.makedirs(p) os.path.exists(p):
                except Exception as e:
                    if verbose():as e:
                        writerr(colored("ERROR processOutput 5: " + str(e), "red"))
                outFile = open(os.path.expanduser(args.output), "w")str(e), "red"))
            except Exception as e:path.expanduser(args.output), "w")
                if vverbose():s e:
                    writerr(colored("ERROR processOutput 2: " + str(e), "red"))    
                    writerr(colored("ERROR processOutput 2: " + str(e), "red"))    
        # Initialize reusable session object for sending requests to the proxy
        sendToProxy = Falsele session object for sending requests to the proxy
        if args.proxy:False
            # Support all proxy protocols
            if not re.match(r'^(http|https|socks4|socks5)://', args.proxy):
                proxy_url = 'http://' + args.proxy
            else:   "https": args.proxy,
                proxy_url = args.proxy
                urllib3.disable_warnings(category=InsecureRequestWarning)
            proxies = {sendToProxy = True
                "http": proxy_url,
                "https": proxy_url,
            }oint in allEndpoints:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            sendToProxy = Truecified, write to the file
            
        # Output all endpointsle.write(endpoint + '\n')
        for endpoint in allEndpoints:
            try: not specified, output to STDOUT
                # If an output file was specified, write to the file) or args.output is None:
                if args.output is not None:oint,True)
                    outFile.write(endpoint + '\n')
                else:    err(colored('ERROR processOutput 6: Could not output links found - ' + str(e), 'red'))
                    # If output is piped or the --output argument was not specified, output to STDOUT
                    if not sys.stdin.isatty() or args.output is None: argument is passed, send the link to the specified proxy
                        write(endpoint,True)oProxy:
            except Exception as e:
                writerr(colored('ERROR processOutput 6: Could not output links found - ' + str(e), 'red'))
                    ts.get(
            # If the -proxy argument is passed, send the link to the specified proxy
            if sendToProxy:ts=True,
                try:
                    # Make the request
                    resp = requests.get(   headers = {"User-Agent": "xnldorker by @xnl-h4ck3r"},
                        endpoint,)
                        allow_redirects=True,
                        verify=False,
                        proxies=proxies,
                        headers = {"User-Agent": "xnldorker by @xnl-h4ck3r"}, Proxy ] Proxy disabled. Check value {args.proxy} is correct.", "red"))
                    )        sendToProxy = False
                    
                except Exception as e:ose the output file if it was opened
                    writerr(colored(f"[ Proxy ] Failed to send {endpoint} to proxy: {str(e)}", "red"))
                    writerr(colored(f"[ Proxy ] Proxy disabled. Check value {args.proxy} is correct.", "red"))one:
                    sendToProxy = False
            rite(colored('Output successfully appended to file: ', 'cyan')+colored(args.output,'white'))
        # Close the output file if it was opened
        try:te(colored('Output successfully written to file: ', 'cyan')+colored(args.output,'white'))
            if args.output is not None:
                if appendedResults:)
                    write(colored('Output successfully appended to file: ', 'cyan')+colored(args.output,'white'))
                else:'ERROR processOutput 3: ' + str(e), 'red'))
                    write(colored('Output successfully written to file: ', 'cyan')+colored(args.output,'white'))  
                write()
                outFile.close()        writerr(colored('ERROR processOutput 1: ' + str(e), 'red'))
        except Exception as e:
            writerr(colored('ERROR processOutput 3: ' + str(e), 'red'))
                            al sourcesToProcess, inputDork
    except Exception as e:
        writerr(colored('ERROR processOutput 1: ' + str(e), 'red'))
tDork, 'magenta')+colored(' The dork to used to search on the sources.','white'))
def showOptionsAndConfig():
    global sourcesToProcess, inputDorkrite(colored('-o: ' + args.output, 'magenta')+colored(' Where gathered endpoints will be written.','white'))
    try:
        write(colored('Selected options:', 'cyan'))
        write(colored('-i: ' + inputDork, 'magenta')+colored(' The dork to used to search on the sources.','white'))ow: " + str(args.output_overwrite), "magenta")+colored(" Whether the output will be overwritten if it already exists.", "white" ))
        if args.output is not None:
            write(colored('-o: ' + args.output, 'magenta')+colored(' Where gathered endpoints will be written.','white')) + args.sources, 'magenta')+colored(' The sources requested to search.','white'))
        else:
            write(colored('-o: <STDOUT>', 'magenta')+colored(' An output file wasn\'t given, so output will be written to STDOUT.','white')).exclude_sources, 'magenta')+colored(' The sources excluded from the search.','white'))
        write(colored("-ow: " + str(args.output_overwrite), "magenta")+colored(" Whether the output will be overwritten if it already exists.", "white" ))
        if args.sources:rite(colored('-cs: ALL', 'magenta')+colored(' The browser timeout in seconds','white'))
            write(colored('-s: ' + args.sources, 'magenta')+colored(' The sources requested to search.','white'))
        if args.exclude_sources:sources that will be searched at a time.','white'))
            write(colored('-es: ' + args.exclude_sources, 'magenta')+colored(' The sources excluded from the search.','white'))
        if args.concurrent_sources == 0:
            write(colored('-cs: ALL', 'magenta')+colored(' The browser timeout in seconds','white'))'-rwos: ' + str(args.resubmit_without_subs), 'magenta')+colored(' Whether the query will be resubmitted, but excluding the sub domains found in the first search.','white'))
        else:
            write(colored('-cs: ' + str(args.concurrent_sources), 'magenta')+colored(' The number of concurrent sources that will be searched at a time.','white'))-proxy: ' + str(args.proxy), 'magenta')+colored(' The proxy to send found links to.','white'))
        write(colored('-t: ' + str(args.timeout), 'magenta')+colored(' The browser timeout in seconds','white'))
        write(colored('-sb: ' + str(args.show_browser), 'magenta')+colored(' Whether the browser will be shown. If False, then headless mode is used.','white')) proxy list to rotate through when encountering CAPTCHA.','white'))
        write(colored('-rwos: ' + str(args.resubmit_without_subs), 'magenta')+colored(' Whether the query will be resubmitted, but excluding the sub domains found in the first search.','white'))ored('Sources being checked: ', 'magenta')+str(sourcesToProcess))
        if args.proxy:write('')
            write(colored('-proxy: ' + str(args.proxy), 'magenta')+colored(' The proxy to send found links to.','white'))
        if args.proxy_list:
            write(colored('-pl: ' + str(args.proxy_list), 'magenta')+colored(' The proxy list to rotate through when encountering CAPTCHA.','white'))        writerr(colored('ERROR showOptionsAndConfig 1: ' + str(e), 'red'))    
        write(colored('Sources being checked: ', 'magenta')+str(sourcesToProcess))
        write('')-s and -es
        
    except Exception as e:s to get individual sources
        writerr(colored('ERROR showOptionsAndConfig 1: ' + str(e), 'red'))        sources = value.split(',')

# For validating arguments -s and -es
def argcheckSources(value):for source in sources):
    # Split the value by commas to get individual sources
    sources = value.split(',')   f"Invalid sources requested. Can only be a combination of {','.join(SOURCES)}"

    # Check if all sources are valid and exist in SOURCESreturn value
    if not all(source.strip() in SOURCES for source in sources):
        raise argparse.ArgumentTypeError(
            f"Invalid sources requested. Can only be a combination of {','.join(SOURCES)}"s from either a file or a comma-separated string"""
        )es
    return valueproxies = []
    
def load_proxies(proxy_list):
    """Load proxies from either a file or a comma-separated string"""th.isfile(proxy_list):
    global proxies
    proxies = []st, 'r') as f:
    
    # Check if the input is a file
    if os.path.isfile(proxy_list):
        try:
            with open(proxy_list, 'r') as f:tps|socks4|socks5)://', line):
                for line in f: + line
                    line = line.strip()roxies.append(line)
                    if line and not line.startswith('#'):
                        # Ensure proxy has correct format (add http:// if missing)d(f'Loaded {len(proxies)} proxies from file', 'green'))
                        if not line.startswith('http://') and not line.startswith('https://'):
                            line = 'http://' + line   writerr(colored(f'Error loading proxies from file: {str(e)}', 'red'))
                        proxies.append(line)
            if verbose():
                writerr(colored(f'Loaded {len(proxies)} proxies from file', 'green'))st.split(','):
        except Exception as e:.strip()
            writerr(colored(f'Error loading proxies from file: {str(e)}', 'red'))
    else:
        # Treat as comma-separated listttp|https|socks4|socks5)://', p):
        for p in proxy_list.split(','): + p
            p = p.strip()es.append(p)
            if p:
                # Ensure proxy has correct format (add http:// if missing)writerr(colored(f'Loaded {len(proxies)} proxies from command line', 'green'))
                if not p.startswith('http://') and not p.startswith('https://'):
                    p = 'http://' + p    return len(proxies) > 0
                proxies.append(p)
        if verbose():
            writerr(colored(f'Loaded {len(proxies)} proxies from command line', 'green')) in a round-robin fashion"""
            global proxies, current_proxy_index
    return len(proxies) > 0

def get_next_proxy():return None
    """Get the next proxy from the list in a round-robin fashion"""
    global proxies, current_proxy_indexy_index + 1) % len(proxies)
        return proxies[current_proxy_index]
    if not proxies:
        return Nonec def run_main():
        
    current_proxy_index = (current_proxy_index + 1) % len(proxies)global args, sourcesToProcess, allSubs, inputDork, proxies
    return proxies[current_proxy_index]
e handler() function when SIGINT is received
async def run_main():signal(SIGINT, handler)
    
    global args, sourcesToProcess, allSubs, inputDork, proxies
    
    # Tell Python to run the handler() function when SIGINT is received   description='xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines.'    
    signal(SIGINT, handler)
    d_argument(
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='xnldorker - by @Xnl-h4ck3r: Gather results of dorks across a number of search engines.'    
    )   help='A dork to use on the search sources.'
    parser.add_argument(
        '-i',d_argument(
        '--input',
        action='store',
        help='A dork to use on the search sources.'
    )   help='The output file that will contain the results (default: output.txt). If piped to another program, output will be written to STDOUT instead.',
    parser.add_argument(
        '-o',_argument(
        '--output',
        action='store',,
        help='The output file that will contain the results (default: output.txt). If piped to another program, output will be written to STDOUT instead.',
    )   help="If the output file already exists, it will be overwritten instead of being appended to.",
    parser.add_argument(
        "-ow",_argument(
        "--output-overwrite",
        action="store_true",
        help="If the output file already exists, it will be overwritten instead of being appended to.",
    )   help='Show the source of each endpoint in the output. Each endpoint will be prefixed, e.g. "[ Bing ] https://example.com".',
    parser.add_argument(
        '-os',d_argument(
        '--output-sources',
        action='store_true',
        help='Show the source of each endpoint in the output. Each endpoint will be prefixed, e.g. "[ Bing ] https://example.com".',
    )s to use when searching (-s duckduckgo,bing). Use -ls to display all available sources.',
    parser.add_argument(es,
        '-s',   metavar='string[]'
        '--sources',
        action='store',_argument(
        help='Specific sources to use when searching (-s duckduckgo,bing). Use -ls to display all available sources.',
        type=argcheckSources,ces',
        metavar='string[]'
    )s to exclude searching (-s google,startpage). Use -ls to display all available sources.',
    parser.add_argument(es,
        '-es',   metavar='string[]'
        '--exclude-sources',
        action='store',_argument(
        help='Specific sources to exclude searching (-s google,startpage). Use -ls to display all available sources.',
        type=argcheckSources,ources",
        metavar='string[]'
    ) number of sources to search at the same time (default: 2). Passing 0 will run ALL specified sources at the same time (this could be very resource intensive and affect results).",
    parser.add_argument(
        "-cs",   default=2,
        "--concurrent-sources",
        action="store",_argument(
        help="The number of sources to search at the same time (default: 2). Passing 0 will run ALL specified sources at the same time (this could be very resource intensive and affect results).",
        type=int,
        default=2,
    )   help='List all available sources.',
    parser.add_argument(
        '-ls',
        '--list-sources',d_argument(
        action='store_true',
        help='List all available sources.',
    )o wait for the source to respond (default: " + str(default_timeout) + " seconds).",
    default_timeout = 30efault_timeout,
    parser.add_argument(
        "-t",   metavar="<seconds>",
        "--timeout",
        help="How many seconds to wait for the source to respond (default: " + str(default_timeout) + " seconds).",_argument(
        default=default_timeout,
        type=int,
        metavar="<seconds>",
    )   help='View the browser instead of using headless browser.',
    parser.add_argument(
        '-sb',
        '--show-browser',argument(
        action='store_true',
        help='View the browser instead of using headless browser.',
    )ds to wait when the -sb option was used and a known anti-bot mechanism is encountered. This is the time you have to manually respond to the anti-bot mechanism before it tries to continue.",
    default_abt = 90efault_abt,
    parser.add_argument(
        "-abt",   metavar="<seconds>",
        "--antibot-timeout",
        help="How many seconds to wait when the -sb option was used and a known anti-bot mechanism is encountered. This is the time you have to manually respond to the anti-bot mechanism before it tries to continue.",rgument(
        default=default_abt,
        type=int,subs',
        metavar="<seconds>",
    )   help='After the initial search, search again but exclude all subs found previously to get more links.',
    parser.add_argument(
        '-rwos',gument(
        '--resubmit-without-subs',
        action='store_true',
        help='After the initial search, search again but exclude all subs found previously to get more links.',the links found to a proxy, e.g http://127.0.0.1:8080",
    )   default="",
    parser.add_argument(
        "-proxy",_argument(
        action="store",
        help="Send the links found to a proxy, e.g http://127.0.0.1:8080",
        default="",
    )to a file containing proxies (one per line) or a comma-separated list of proxies to rotate through when encountering CAPTCHA.",
    parser.add_argument(   default="",
        "-pl",
        "--proxy-list",
        action="store",ol banner.')
        help="Path to a file containing proxies (one per line) or a comma-separated list of proxies to rotate through when encountering CAPTCHA.",
        default="",
    ) '--vverbose', action='store_true', help='Increased verbose output.')
    parser.add_argument('--debug', action='store_true', help='Save page contents on error.')    args = parser.parse_args()
    parser.add_argument('-nb', '--no-banner', action='store_true', help='Hides the tool banner.')
    parser.add_argument('--version', action='store_true', help='Show version number')as passed, display version and exit
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    parser.add_argument('-vv', '--vverbose', action='store_true', help='Increased verbose output.')red('xnldorker - v' + __version__,'cyan'))
    args = parser.parse_args()    sys.exit()

    # If --version was passed, display version and exitas passed, display sources and exit
    if args.version:
        write(colored('xnldorker - v' + __version__,'cyan'))anner:
        sys.exit()
    red('These are the available sources: ','green')+str(SOURCES))
    # If --list-sources was passed, display sources and exitsys.exit()
    if args.list_sources:
        if not args.no_banner:
            showBanner()n, raise an error
        write(colored('These are the available sources: ','green')+str(SOURCES))
        sys.exit()
        lored('You need to provide input with -i argument or through <stdin>. This will be a dork used to search the requested sources, e.g. "site:example.com"', 'red'))
    try:        sys.exit()
        # If no input was given, raise an error
        if sys.stdin.isatty():to process
            if args.input is None:
                writerr(colored('You need to provide input with -i argument or through <stdin>. This will be a dork used to search the requested sources, e.g. "site:example.com"', 'red'))ourcesToProcess = SOURCES
                sys.exit()
        split(',')
        # Determine the sources to process
        if args.sources is None:            sourcesToProcess = [source for source in sourcesToProcess if source not in args.exclude_sources]
            sourcesToProcess = SOURCES
        else:depending on the input type
            sourcesToProcess = args.sources.split(',')
        if args.exclude_sources is not None:nputDork = args.input
            sourcesToProcess = [source for source in sourcesToProcess if source not in args.exclude_sources]
    inputDork = sys.stdin.readline().strip()
        # Get the input dork, depending on the input type
        if sys.stdin.isatty():o spaces, assume it is a domain only and prefix with "site:"
            inputDork = args.input inputDork, re.IGNORECASE) and ' ' not in inputDork:
        else:inputDork = 'site:'+inputDork
            inputDork = sys.stdin.readline().strip()
        d, show the banner, and if --verbose option was chosen show options and config values
        # If the input value doesn't seem to start with an advanced search operator and has no spaces, assume it is a domain only and prefix with "site:"
        if not re.match(r'(^|\s)[a-z]*:', inputDork, re.IGNORECASE) and ' ' not in inputDork:equested to hide
            inputDork = 'site:'+inputDorkanner:
            r()
        # If input is not piped, show the banner, and if --verbose option was chosen show options and config values
        if sys.stdin.isatty():        showOptionsAndConfig()
            # Show banner unless requested to hide
            if not args.no_banner: proxy list was provided
                showBanner()
            if verbose():
                showOptionsAndConfig()writerr(colored(f'Loaded {len(proxies)} proxies for rotation', 'green'))
        
        # Load proxies if a proxy list was provided-i (--input), or <stdin>
        if args.proxy_list:        await processInput(inputDork)
            if load_proxies(args.proxy_list) and verbose():
                writerr(colored(f'Loaded {len(proxies)} proxies for rotation', 'green'))-without-subs was passed, then run again with subdomains removed
                
        # Process the input given on -i (--input), or <stdin>
        await processInput(inputDork) again for input: ', 'magenta')+colored(inputDork,'white'))
    await processInput(inputDork)
        # If there were some subs found, and the --resubmit-without-subs was passed, then run again with subdomains removed
        if len(allSubs) > 0 and args.resubmit_without_subs:ls with parameters
            inputDork = inputDork + ' ' + ' '.join(['-{}'.format(sub) for sub in allSubs if sub])await processOutput()
            write(colored('\nResubmitting again for input: ', 'magenta')+colored(inputDork,'white'))
            await processInput(inputDork)
                writerr(colored('ERROR main 1: ' + str(e), 'red'))      
        # Output the saved urls with parameters
        await processOutput()ow ko-fi link if verbose and not piped
        
    except Exception as e:
        writerr(colored('ERROR main 1: ' + str(e), 'red'))       writerr(colored('✅ Want to buy me a coffee? ☕ https://ko-fi.com/xnlh4ck3r 🤘', 'green'))

    # Show ko-fi link if verbose and not piped        pass
    try:
        if verbose() and sys.stdin.isatty():
            writerr(colored('✅ Want to buy me a coffee? ☕ https://ko-fi.com/xnlh4ck3r 🤘', 'green'))asyncio.run(run_main())
    except:
        pass_ == '__main__':
    main()






    main()if __name__ == '__main__':        asyncio.run(run_main())def main():