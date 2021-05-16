from json import loads
from matrixdraw import MatrixDraw
from os import getcwd
from os.path import join
from sys import stdout
from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from traceback import format_exc
from wshandler import WebSocket

import logging

def initialize():
	try:
		settings = loads(open("appsettings.json").read())
		ls = settings["logging"]
		logging.basicConfig(
				format=ls["format"],
				level=logging.getLevelName(ls["level"]),
				handlers = [
					logging.FileHandler(ls["dir"]),
					logging.StreamHandler(stdout)])

		artist = MatrixDraw(settings["matrix"])	
		logging.info("Initialized")
		return artist

	except Exception:
		logging.error(f"Not initialized: {format_exc()}")
		raise

def start(artist):
	try:
		server = Application([
			(r'/websocket', WebSocket, { "artist": artist }),
			(r'/(.*)', StaticFileHandler, {
				"path": join(getcwd(), "site"), 
				"default_filename": "index.html" })])

		server.listen(5678)
		logging.info("Starting server")
		IOLoop.instance().start()

	except Exception:
		logging.error(f"Server not started: {format_exc()}")
		raise

if __name__ == "__main__":
	start(initialize())

