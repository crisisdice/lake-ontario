from matrixdraw import MatrixDraw
from matrixstore import MatrixStore
from os import getcwd
from os.path import join
from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.options import define, options
from traceback import format_exc
from wshandler import WebSocket

import logging

def start():
	try:
		logging.basicConfig(format="[%(threadName)s] %(levelname)s: %(message)s")
		logging.root.level = logging.getLevelName(options.loglevel)

		logging.debug("DEBUG activated")

		artist = MatrixDraw(MatrixStore())

		server = Application([
			(r'/websocket', WebSocket, { "artist": artist, "options": options }),
			(r'/(.*)', StaticFileHandler, {
				"path": join(getcwd(), "site"), 
				"default_filename": "index.html" })])

		ioloop = IOLoop.instance()

		logging.info("Artist and server initialized")

		if options.seed:
			ioloop.spawn_callback(seed)

		server.listen(options.port)
		logging.info("Starting server")
		ioloop.start()

	except Exception:
		logging.error(f"Server not started: {format_exc()}")
		raise

def seed():
	logging.info("Seeding .mat files")
	tempstore = MatrixStore()
	tempstore.seed(options.seed.split(','), options.steps)
	logging.info("Finished seeding .mat files")

if __name__ == "__main__":
	#define options
	define("port", default="8000", help="Listening port")
	define("seed", default="", help="Comma delimited seasons to calculate .mat files for")
	define("loglevel", default="INFO", help="Python log level")
	define("steps", default=10, help="Amount of time steps to calculate and show")
	define("dim", default=4732, help="Transition matrix row size")
	define("seasons", default="spring,summer,fall,winter", help="Comma delimited seasons to show")
	define("cmap", default="plasma", help="Matplotlib colormap to apply to matrix")
	#TODO recompile svg for new cmap and html for seasons

	options.parse_command_line()

	start()

