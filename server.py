from json import loads
from matrixdraw import MatrixDraw
from matrixstore import MatrixStore
from os import getcwd
from os.path import join
from sys import stdout
from tornado.web import Application, StaticFileHandler
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from tornado.options import define, options
from traceback import format_exc
from wshandler import WebSocket

import logging

def seed():
	settings = loads(open("appsettings.json").read())
	logging.info("Seeding database")
	store = MatrixStore()
	store.seed(settings["seasons"], settings["steps"])

def initialize():
	try:
		settings = loads(open("appsettings.json").read())

		logging.basicConfig(
				format=settings["logging_format"],
				level=logging.getLevelName(settings["logging_level"]),
				handlers = [logging.StreamHandler(stdout)])

		store = MatrixStore()
		artist = MatrixDraw(store)

		logging.info("Initialized")

		return (artist, settings)

	except Exception:
		logging.error(f"Not initialized: {format_exc()}")
		raise

def start(artist, settings):
	try:
		server = Application([
			(r'/websocket', WebSocket, { "artist": artist, "settings": settings }),
			(r'/(.*)', StaticFileHandler, {
				"path": join(getcwd(), "site"), 
				"default_filename": "index.html" })])
		ioloop = IOLoop.instance()
		if options.seed:
			ioloop.spawn_callback(seed)
		server.listen(options.port)
		logging.info("Starting server")
		ioloop.start()

	except Exception:
		logging.error(f"Server not started: {format_exc()}")
		raise

if __name__ == "__main__":
	#define options
	define("port", default="8000", help="Listening port", type=str)
	define("seed", default=False, help="Seed database with matricie")
	define("remote", default=False, help="Use remote database instance")
	options.parse_command_line()

	start(*initialize())

