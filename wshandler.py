from json import dumps, loads
from json.decoder import JSONDecodeError
from logging import debug, error, info
from tornado.iostream import StreamClosedError
from tornado.gen import coroutine, sleep
from tornado.websocket import WebSocketHandler, WebSocketClosedError


class WebSocket(WebSocketHandler):
	def initialize(self, artist):
		self.artist = artist
		self.ip = self.request.remote_ip

	def open(self):
		info(f"Connection from {self.ip}")

	@coroutine
	def on_message(self, message):
		try:
			body = loads(message)
			self.artist.validate_matrix_request(body["node"], body["season"])
			sv = self.artist.get_state_vector(body["node"])
			info(f"Processing {message} from {self.ip}")
	
			for step in range (1, self.artist.steps):
				result = yield self.draw_task(sv, step)
				yield self.write_message(dumps({ "nodes": result }))
	
			self.close()

		except (WebSocketClosedError, StreamClosedError):
			debug(f"Connection from {self.ip} closed by client")
		except (KeyError, ValueError, JSONDecodeError):
			error(f"Faulty request {message} from {self.ip}")

	@coroutine
	def draw_task(self, state_vector, step):
		frame = self.artist.draw_frame(state_vector, step)
		yield sleep(0.5)
		return frame
