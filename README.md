# JHU Domain Crawler + Search Engine

## Crawler

## Search Engine

Run the CLI app via `python3 query.py`.

To run the Web app, first start the backend server:

Create and enter into a Python virtual environment, and then install
dependencies. For more information and for the Windows commands, please refer to
the [official docs](https://flask.palletsprojects.com/en/3.0.x/installation).

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install flask flask-cors numpy nltk
```

In the venv, run the following command to start the Flask server:

```bash 
flask run
```

The server is now running and will be used to serve data to the frontend.

Ctrl-C to exit the server and `deactivate` to exit the virtual environment.

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

A [screenshot](./webapp.png) of the website is included with this
submission for your reference.

Let us know at any point if you have issues running the code. Thank you very
much!
