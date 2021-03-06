from json import dumps, loads
from json.decoder import JSONDecodeError
from logging import debug, error, info
from tornado.iostream import StreamClosedError
from tornado.gen import coroutine, sleep
from tornado.websocket import WebSocketHandler, WebSocketClosedError


class WebSocket(WebSocketHandler):
	def initialize(self, artist, options):
		self.artist = artist
		self.seasons = options.seasons.split(',')
		self.steps = options.steps
		self.dim = options.dim
		self.cmap = options.cmap

		#TODO get ip from heroku header
		self.ip = self.request.remote_ip

	def open(self):
		info(f"Connection from {self.ip}")

	@coroutine
	def on_message(self, message):
		try:
			body = loads(message)

			node = body["node"]
			season = body["season"]
			intensity = body["intensity"]

			self.validate_matrix_request(node, season, intensity)
			info(f"Processing {message} from {self.ip}")
			sv = self.artist.get_state_vector(node, intensity, self.dim)
	
			for step in range(1, self.steps):
				result = yield self.draw_task(sv, season, step)
				yield self.write_message(dumps({ "nodes": result }))
	
			self.close()

		except (WebSocketClosedError, StreamClosedError):
			debug(f"Connection from {self.ip} closed by client")
		except (KeyError, ValueError, JSONDecodeError):
			error(f"Faulty request {message} from {self.ip}")
		except Exception as ex:
			error(ex)
		finally:
			info(f"Finished with {self.ip}")

	@coroutine
	def draw_task(self, state_vector, season, step):
		frame = self.artist.draw_frame(state_vector, season, step, self.cmap)
		yield sleep(0)
		return frame

	def validate_matrix_request(self, node, season, intensity):
		valid_node = type(node) == int and node > -1 and node < self.dim
		valid_season = season in self.seasons
		valid_intensity = type(intensity) == int and intensity % 2 == 0 and intensity > 0 and intensity < 11

		if not valid_node or not valid_season:
			raise ValueError()
