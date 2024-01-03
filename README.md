# uniparser-web

This is a simple web interface for runninig ``uniparser`` analyzers on the server to analyze the sentences the user can input in the web interface. The HTML output is in table format.

## Installation 

Firstly, clone this repository:
```
git clone https://github.com/timarkh/uniparser-web.git
```

Then install dependencies:
```
cd uniparser-web
pip install -r requirements.txt
```

And now run web-app:
```
python3 uniparser-web.wsgi
```
The web application will be available on http://127.0.0.1:5000.
