from json import loads
from matrixdraw import MatrixDraw
from matrixstore import MatrixStore
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

		logging.basicConfig(
				format=settings["logging"]["format"],
				level=logging.getLevelName(settings["logging"]["level"]),
				handlers = [logging.StreamHandler(stdout)])

		store = MatrixStore(settings["matrix"], options.remote)

		if options.seed:
			logging.info("Seeding database")
			store.seed()

		artist = MatrixDraw(settings["matrix"], store)

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

		server.listen(options.port)
		logging.info("Starting server")
		IOLoop.instance().start()

	except Exception:
		logging.error(f"Server not started: {format_exc()}")
		raise

if __name__ == "__main__":
	#define options
	define("port", default="8000", help="Listening port", type=str)
	define("seed", default=False, help="Seed database with matricie")
	define("remote", default=False, help="Use remote database instance")
	options.parse_command_line()

	start(initialize())

