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

    parsed_url = parse.urlparse(url)  # parse the URL for comparison
    links = get_links(url)
    filtered = []
    for link, title in links:
        parsed_link = parse.urlparse(link)  # parse each extracted link
        if parsed_link.netloc != parsed_url.netloc or parsed_link.path != parsed_url.path:
            # keep links with different domains or paths
            filtered.append((link, title))
    return filtered


def queueCrawl(root, wanted_content=[], within_domain=True, limit_words=150, max_pages=1000):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    Here we are using queue to implement FIFO strategy for crawling.
    '''

    queue = Queue()  # use queue

    queue.put((root,''))

    visited = []
    extracted = []
    cnt = 0
    while not queue.empty() and cnt < max_pages:
        cnt += 1
        url, title = queue.get()  

        # skip if already visited
        while url in visited and not queue.empty():
            url, title = queue.get()
        
        path = parse.urlparse(url).path

        # skip certain less informative paths
        if path in ["/experts/", "/at-work/milestones/", "/at-work/cheers/"]:
            continue

        try:
            req = request.urlopen(url)
            html = req.read().decode('utf-8')
            content_type = req.headers['Content-Type']

            # if content type is specified and not wanted, skip
            if len(wanted_content) > 0 and content_type not in wanted_content:
                continue

            visited.append(url)
            visitlog.debug(url)
            parsed_url = parse.urlparse(url) #keep for later comparison

            ntitle,author,content = extract_information(url, html, limit_words)
            extracted.append(url)

            # additional filtering to avoid multiple lines
            title_filtered = title.replace('\n', ' ')
            title_sep = title_filtered + '' if title_filtered == '' else ' '
            extracted.append(title_sep + ntitle.replace('\n', ' '))
            extracted.append(author.replace('\n', ' '))
            extracted.append(content.replace('\n', ' '))
            extractlog.debug(content)

            for link, title in get_nonlocal_links(url):
                # if self reference, skip
                if within_domain and parsed_url.netloc != parse.urlparse(link).netloc:
                    continue

                # skip those if visited or void links
                if link in visited or link.startswith("javascript:"):
                    continue

                queue.put((link, title))  # Add link to the queue

        except Exception as e:
            print(e, url)

    return visited, extracted

def stackCrawl(root, wanted_content=[], within_domain=True, limit_words=150, max_pages=1000):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    Here we are using stack to implement LIFO strategy for crawling.
    '''

    stack = []  # use stack

    stack.append((root,''))

    visited = []
    extracted = []
    cnt = 0
    while stack and cnt < max_pages:
        cnt += 1
        url, title = stack.pop()  

        # skip if already visited
        while url in visited and stack:
            url, title = stack.pop()
        
        path = parse.urlparse(url).path

        # skip certain less informative paths
        if path in ["/experts/", "/at-work/milestones/", "/at-work/cheers/"]:
            continue

        try:
            req = request.urlopen(url)
            html = req.read().decode('utf-8')
            content_type = req.headers['Content-Type']

            # if content type is specified and not wanted, skip
            if len(wanted_content) > 0 and content_type not in wanted_content:
                continue

            visited.append(url)
            visitlog.debug(url)
            parsed_url = parse.urlparse(url) # keep for later comparison

            ntitle,author,content = extract_information(url, html, limit_words)
            extracted.append(url)

            # additional filtering to avoid multiple lines
            title_filtered = title.replace('\n', ' ')
            title_sep = title_filtered + '' if title_filtered == '' else ' '
            extracted.append(title_sep + ntitle.replace('\n', ' '))
            extracted.append(author.replace('\n', ' '))
            extracted.append(content.replace('\n', ' '))
            extractlog.debug(content)

            for link, title in get_nonlocal_links(url):
                # if self reference, skip
                if within_domain and parsed_url.netloc != parse.urlparse(link).netloc:
                    continue

                # skip those if visited or void links
                if link in visited or link.startswith("javascript:"):
                    continue

                stack.append((link, title))  # add link to the queue

        except Exception as e:
            print(e, url)

    return visited, extracted


def extract_information(url, html, limit_words):
    '''Extract information from HTML, returning a single piece of text
       containing the title, author, and content of the article.
       Extra engineering is done for JHU websites.
       limit_words is the maximum number of words to return for each content.
    '''

    # extract all text content from the HTML document
    soup = BeautifulSoup(html, 'html.parser')

    # adjustments to newsletter crawling
    if('jhunewsletter' in url):
        
        if soup.title is not None:
            title = soup.title.string.strip()
        else:
            title = ''
        if soup.find('p', class_ = 'authors') is not None:
            author_name = soup.find('p', class_ = 'authors').text.strip()
        else:
            author_name = ""
        if soup.find("div", class_="article-content") is not None:
            article_content = soup.find("div", class_="article-content").text.strip()
        else:
            article_content = soup.get_text().strip()
    # adjustments to hub.jhu.edu crawling
    elif('hub.jhu' in url):
        
        if soup.title is not None:
            title = soup.title.string.strip()
        else:
            title = ''
        if soup.find(class_ = 'author') is not None:
            author_name = soup.find(class_ = 'author').text.strip()
        else:
            author_name = ""
        if soup.find("div", id="main") is not None:
            article_content = soup.find("div", id="main").text.strip()
        else:
            article_content = soup.get_text().strip()
    # adjustments to jhu.edu crawling
    elif('jhu.edu' in url):
        if soup.title is not None:
            title = soup.title.string.strip()
        else:
            title = ''
        author_name = ''
        if soup.find("main") is not None:
            article_content = soup.find("main").text.strip()
        else:
             article_content = soup.get_text().strip()
    # general case; agressive strategies are used, but if fails, it will return back to general crawling.
    else:
        if soup.title is not None:
            title = soup.title.string.strip()
        else:
            title = ''
        if soup.find(class_= 'author') is not None:
            author_name = soup.find(class_ = 'author').text.strip()
        else:
            author_name = ''  
        if soup.find("main") is not None:
            article_content = soup.find("main").text.strip()
        else:
             article_content = soup.get_text().strip()

    # word limit to ensure that the content is not too long
    if limit_words and article_content is not None:
        words = article_content.split()
        text_content = ' '.join(words[:limit_words])

    return title.strip(), author_name.strip(), text_content.strip()



def writelines(filename, data):
    with open(filename, 'w', encoding='utf-8') as fout:
        for d in data:
            print(d, file=fout)


def run(site, wanted_content=[], within_domain=True, limit_words=150, max_pages=1000):
    '''Container function to run the crawler.
       Can choose between queueCrawl or heapCrawl for different strategies.
    '''

    output_file = site + ".latest.txt"

    if os.path.exists(output_file):
        os.remove(output_file) 

    #choose between queueCrawl or stackCrawl
    _, extracted = queueCrawl("https://" + site, wanted_content, within_domain, limit_words, max_pages)
    #_, extracted = stackCrawl("https://" + site, wanted_content, within_domain, limit_words, max_pages)

    writelines(output_file, extracted)

def main():
    if len(sys.argv) < 2:
        print('Usage: python webCrawl.py <URL> [content_type]')
        sys.exit(1)

    site = sys.argv[1]
    wanted_content = sys.argv[2:] if len(sys.argv) > 2 else []
    run(site, wanted_content)

if __name__ == '__main__':
    main()
