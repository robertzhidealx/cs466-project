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
generate {url}.txt containing 1000 crawled pages, with 4 lines per page.  The
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

## Limitations

Crawling and information extraction from other websites might not be as effective, due to
variations in website designs. To achieve higher precision, please try increase the max word
limit and the number of pages to crawl for non-JHU websites.

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
