import asyncio
import functools as f
import json
import logging
import sys
import traceback
import websockets
import websockets.exceptions as wse

from matrixdraw import MatrixDraw

async def handler(websocket, path, artist):
	try:
		ip = websocket.remote_address[0]
		request = await websocket.recv()
		body = json.loads(request)
		sv = artist.get_state_vector(body["node"])

		logging.info(f"Processing {request} from {ip}")

		for step in range (1, artist.steps):
			task = asyncio.create_task(artist.draw_frame(sv, step))
			await websocket.send(json.dumps({ "nodes": await task }))
	except wse.ConnectionClosedError:
		logging.debug(f"Client {ip} closed connection")

def start(artist):
	start_server = websockets.serve(f.partial(handler, artist = artist), "127.0.0.1", 5678)
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
	try:
		logging.basicConfig(
			format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s', 
			level=logging.INFO, 
			handlers = [
				logging.FileHandler("logs/server.log"),
				logging.StreamHandler(sys.stdout)
			]
		)
		md = MatrixDraw()

		logging.info("Initialized and starting server")
	
	except Exception:
		logging.error(f"Not initialized: {traceback.format_exc()}")
		raise

	start(md)

