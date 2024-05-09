import logging
import re
import os
import sys
from bs4 import BeautifulSoup
from queue import Queue, PriorityQueue
from urllib import parse, request

logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')


def parse_links(root, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()
            yield (parse.urljoin(root, link.get('href')), text)


def get_links(url):
    res = request.urlopen(url)
    return list(parse_links(url, res.read()))


def get_nonlocal_links(url):
    '''Get a list of links on the page specificed by the url,
    but only keep non-local links and non self-references.
    Return a list of (link, title) pairs, just like get_links()'''

    parsed_url = parse.urlparse(url)  # Parse the URL for comparison
    links = get_links(url)
    filtered = []
    for link, title in links:
        parsed_link = parse.urlparse(link)  # Parse each extracted link
        if parsed_link.netloc != parsed_url.netloc or parsed_link.path != parsed_url.path:
            # Keep links with different domains or paths
            filtered.append((link, title))
    return filtered


def crawl(root, wanted_content=[], within_domain=True, limit_words=150, max_pages=200):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    '''
    # TODO: implement

    queue = PriorityQueue()  # Use PriorityQueue instead of Queue

    # Calculate priority of the root URL based on the number of slashes, so root directories get visited first
    priority = root.count('/')
    queue.put((priority, root,''))

    visited = []
    extracted = []
    cnt = 0
    while not queue.empty() and cnt < max_pages:
        cnt += 1
        #print(cnt)
        _, url, title = queue.get()  

        #skip if already visited
        while url in visited and not queue.empty():
            _, url, title = queue.get()
        
        #print(url)

        try:
            req = request.urlopen(url)
            html = req.read().decode('utf-8')
            content_type = req.headers['Content-Type']

            #if content type is specified and not wanted, skip
            if len(wanted_content) > 0 and content_type not in wanted_content:
                continue

            visited.append(url)
            visitlog.debug(url)
            #writelines('html.txt', [html])
            parsed_url = parse.urlparse(url) #keep for later comparison

            ntitle,author,content = extract_information(url, html, limit_words)
            extracted.append(url)
            extracted.append(title + ';' + ntitle + ';' + author)
            extracted.append(content)
            extractlog.debug(content)

            for link, title in get_nonlocal_links(url):
                #if self reference, skip
                if within_domain and parsed_url.netloc != parse.urlparse(link).netloc:
                    continue

                #skip those if visited or void links
                if link in visited or link.startswith("javascript:"):
                    continue

                priority = link.count('/')
                queue.put((priority, link, title))  # Add link with priority to the queue

        except Exception as e:
            print(e, url)

    return visited, extracted


def extract_information(url, html, limit_words):
    '''Extract information from HTML, returning a single piece of text'''

    # Extract all text content from the HTML document
    soup = BeautifulSoup(html, 'html.parser')

    if('jhunewsletter' in url):
        title = soup.title.string
        author_name = soup.find('p', class_ = 'authors').text.strip()
        article_content = soup.find("div", class_="article-content").text.strip()
    elif('hub.jhu' in url):
        title = soup.title.string
        author_name = soup.find(class_ = 'author').text
        article_content = print(soup.find("div", id="main").text.strip())
    elif('jhu.edu' in url):
        title = soup.title.string
        author_name = ''
        article_content = soup.find("main").text.strip()
    else:
        if soup.title is not None:
            title = soup.title.string
        else:
            title = ''
        if soup.find(class_= 'author') is not None:
            author_name = soup.find(class_ = 'author').text
        else:
            author_name = ''  
        article_content = soup.get_text()


    if limit_words:
        words = article_content.split()
        text_content = ' '.join(words[:limit_words])

    return title, author_name, text_content.strip()



def writelines(filename, data):
    with open(filename, 'w', encoding='utf-8') as fout:
        for d in data:
            print(d, file=fout)


def run(site, wanted_content=[], within_domain=True, limit_words=150, max_pages=200):
  
    if os.path.exists('extracted.txt'):
        os.remove('extracted.txt')
 
    # links = get_links(site)
    # writelines('links.txt', links)

    # nonlocal_links = get_nonlocal_links(site)
    # writelines('nonlocal.txt', nonlocal_links)

    visited, extracted = crawl(site, wanted_content, within_domain, limit_words ,max_pages)
    #writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)

def main():
    if len(sys.argv) < 2:
        print('Usage: python webCrawl.py <URL> [content_type]')
        sys.exit(1)

    site = sys.argv[1]
    wanted_content = sys.argv[2:] if len(sys.argv) > 2 else []
    run(site, wanted_content)

if __name__ == '__main__':
    main()
