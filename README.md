# uniparser-web

This is a simple web interface for runninig ``uniparser`` analyzers on the server to analyze the sentences the user can input in the web interface. The HTML output is in table format.

## Usage

Clone this repository and install dependencies:
```
git clone https://github.com/timarkh/uniparser-web.git
cd uniparser-web
pip install -r requirements.txt
```

If you are going to run the app locally, all you have to do is launch the ``wsgi`` file:
```
python3 uniparser-web.wsgi
```
The web application will be available at http://127.0.0.1:5000.

If deployed on a server, it is recommended to plug the app into Apache or nginx.

