from json import loads
from matrixdraw import MatrixDraw
from os import getcwd
from os.path import join
from sys import stdout
from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.options import define, options
from traceback import format_exc
from wshandler import WebSocket

import logging

def initialize():
	try:
		settings = loads(open("appsettings.json").read())
		define("port", default="8000", help="Listening port", type=str)
		ls = settings["logging"]
		logging.basicConfig(
				format=ls["format"],
				level=logging.getLevelName(ls["level"]),
				handlers = [logging.StreamHandler(stdout)])

		artist = MatrixDraw(settings["matrix"])	
		logging.info("Initialized")
		return artist

	except Exception:
		logging.error(f"Not initialized: {format_exc()}")
		raise

def start(artist, port):
	try:
		server = Application([
			(r'/websocket', WebSocket, { "artist": artist }),
			(r'/(.*)', StaticFileHandler, {
				"path": join(getcwd(), "site"), 
				"default_filename": "index.html" })])

		server.listen(port)
		logging.info("Starting server")
		IOLoop.instance().start()

	except Exception:
		logging.error(f"Server not started: {format_exc()}")
		raise

if __name__ == "__main__":
	artist = initialize()
	options.parse_command_line()
	start(artist, options.port)

