# Hopkins Search Engine

## Team members

Jiaxuan Zhang (601.666, jzhan239@jhu.edu), Yiyang Li (601.666, yli302@jhu.edu)

Project summary:

Web and CLI apps to help Hopkins students gain easier access to the latest
events, activities, and announcements on campus and within the Hopkins
community. We allow users the options to (1) quickly query pre-crawled data we
update periodically, or (2) crawl the latest info as they search. Both the web
and CLI interface exposes many options (e.g., which high-level domain to search
from) for the users to tweak that allows for fine-grained search control.

GitHub repository: https://github.com/robertzhidealx/cs466-project

## Set up

Create and enter into a Python virtual environment, and then install
dependencies. For more information and for the Windows commands, please refer to
the [official docs](https://flask.palletsprojects.com/en/3.0.x/installation).

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install flask flask-cors numpy nltk bs4
```

`deactivate` to exit the virtual environment.

### Crawler

Run the crawler to prepare the pre-crawled data. The crawler is engineered to 
extract information from websites within domain www.jhu.edu, hub.jhu.edu and 
www.jhunewsletter.com more effectively, while also flexible enough to crawl from
other websites.

To run the crawler by itself, use 'python3 webCrawl.py {url}' (url should be
without the https:// prefix) to crawl websites with default settings. This would
generate {url}.latest.txt containing 1000 crawled pages, with 4 lines per page.  The
first line contains the url, the second line contains the title, the third line
contains the author, and the fourth line contains the preview text.

Crawling could also be done from the web app, generating {url}.latest.txt files,
again with the format specified previously.

### Search Engine

Run the CLI app via `python3 query.py`.

To run the Web app, first enter the venv and start the backend server:

```bash 
. .venv/bin/activate
flask run
```

The server is now running and will be used to serve data to the frontend.

To start the frontend website, open a new terminal and navigate to the
`jhu-search-engine` directory.

This is a JavaScript (Next.js) project, so in order to run it, you need to first
install _the latest_ version of Node.js (>= v18.17.0) and NPM (the Node.js
package manager) by following the instructions
[here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Once done, first install dependencies by running:

```bash
npm install
```

Then, start the frontend by running:

```bash
npm run dev
```

Navigate to `http://localhost:3000` in your browser. Voila!

Let us know at any point if you have issues running our project. Thank you very
much!

## Achievements
- Crawling is optimized to ensure no duplicate access, and in-domain search is ensured
  so we get info only from our desired websites.

- Information extraction is engineered to accurately access desired information
  from JHU websites, increasing efficiency and accuracy for JHU related searches.

- Queue and stack strategies for crawling is implemented, so user could use different
  crawling strategies corresponding to different websites.

- Our web interface is modern and well-designed, providing users with a range of
  options to facilitate deriving the most relevant pages. Pages retrieved are
  ranked from the most relevant to the least relevant, whether it's the web app
  or the CLI app. The search button on the web app gets disabled when crawling
  is in progress, thus preventing the user from starting another crawl when the
  current one has not finished. This follows best practices in design. The
  retrieved entries additionally show their index in all the pages crawled and
  their corresponding URL for easy reference of the actual page.

- We give the users maximum flexibility by not only providing the JHU Hub and
  the JHU Newsletter as options to crawl and search from, but also arbitrary
  domains as specified by users. Again, they may do this on our intuitively
  designed web interface via a dropdown menu.

- We provide multiple modailities of interaction with our tool, both through a
  web graphical user interface and through a CLI tool. For users more accustomed
  to GUIs, the web app is the way to go; for those who want a quick search, the
  CLI tool can be a good option.

- On the web app, users may choose if they want to search using the pre-crawled
  dataset or crawl the latest data on the fly. The pros and cons of each option
  are obvious: with the former, info retrieval is much faster but data may not
  be the most up to date; with the latter, you get the most recent events but at
  the cost of much slower runtime - crawling 100 pages take 30s to a minute, on
  our end.

- We designed our tool based on the client-server architecture, with clear-cut
  APIs bridging the two. As a result, we are able to use a common set of
  functions to serve the web frontend and the CLI frontend, including functions
  related to info retrieval and those related to web crawling.

- We allow search pages based on their title, author, and preview text (which is
  part of the main body text), and additionally select whether to remove
  stopwords, stem words, compute term weights using IDF, TF-IDF, or Boolean,
  compute similarity using cosine, jaccard, dice, or overlap, which relative
  weighting scheme to use across the three fields, and how many top pages to
  retrieve.

- On the web app, if a user wants to crawl on the fly, they may specify the
  number of pages they want to the crawler to stop with, depending on how much
  time they have on their hands.

## Limitations

- Crawling and information extraction from other websites might not be as
  effective, due to variations in website designs. That said, we tried our best
  to come up with a general purpose HTML search scheme to find fields like the
  author of an article. To achieve higher precision, one may try to increase the
  max word limit and the number of pages to crawl for non-JHU websites.

- Our web app UI can be improved by the addition of a paging system, instead of
  having the user scroll all the way down for certain entries.

- A perma-link from within our web app can be provided for each retrieved entry,
  for easier sharing with others. This feature will require very careful
  engineering thanks to the dynamic nature of our search engine. We didn't
  explore this due to time constraints.

- It takes a while to crawl pages, thus it would be a nice extension to
  parallelize this process to give users real-time feedback while crawling is in
  progress.

## Screenshots

A [screenshot](./webapp.png) of the website is included with this
submission for your reference.

TODO: add more

## Empirical evaluation

Since our tool is essentially a search engine, there is no obvious metric by
which we can evaluate its effectiveness against real-time data.

## Notes

Besides the Python/JavaScript libraries we utilize, all code was written by the
two of us (based to some extent on skeletons provided in prior assignments of
this course). 
