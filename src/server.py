import asyncio
import functools as f
import json
import json.decoder as jsd
import logging
import sys
import traceback
import websockets
import websockets.exceptions as wse

from matrixdraw import MatrixDraw

async def handler(websocket, path, artist):
	try:
		ip = websocket.remote_address[0]

		logging.info(f"Connection from {ip}")

		request = await websocket.recv()
		body = json.loads(request)

		artist.validate_matrix_request(body["node"], body["season"])

		sv = artist.get_state_vector(body["node"])

		logging.info(f"Processing {request} from {ip}")

		for step in range (1, artist.steps):
			task = asyncio.create_task(artist.draw_frame(sv, step))
			await websocket.send(json.dumps({ "nodes": await task }))
	except wse.ConnectionClosedError:
		logging.debug(f"Client {ip} closed connection")
	except (KeyError, ValueError, jsd.JSONDecodeError):
		logging.error(f"Faulty request {request} from {ip}")

def initialize():
	try:
		settings = json.loads(open("appsettings.json").read())
		ls = settings["logging"]
		logging.basicConfig(
				format=ls["format"],
				level=logging.getLevelName(ls["level"]),
				handlers = [
					logging.FileHandler(ls["dir"]),
					logging.StreamHandler(sys.stdout)
		])
		artist = MatrixDraw(settings["matrix"])

		logging.info("Initialized")

		return (artist, settings)
	except Exception:
		logging.error(f"Not initialized: {traceback.format_exc()}")
		raise

def start(artist, settings):
	try:
		logging.info("Starting server")

		start_server = websockets.serve(
			f.partial(handler, artist = artist),
			settings["origin"],
			settings["socket_port"]
		)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	except Exception:
		logging.error(f"Server not started: {traceback.format_exc()}")
		raise

if __name__ == "__main__":
	start(*initialize())

