import asyncio
import functools as f
import json
import websockets
import websockets.exceptions as wse

from matrixdraw import MatrixDraw

async def handler(websocket, path, artist):
	try:
		request = await websocket.recv()
		body = json.loads(request)
		sv = artist.get_state_vector(body["node"])
		print(f"Processing {request}")
		for step in range (1, artist.steps):
			task = asyncio.create_task(artist.draw_frame(sv, step))
			await websocket.send(json.dumps({ "nodes": await task }))

	except wse.ConnectionClosedError:
		print("Client closed connection")

if __name__ == "__main__":
	md = MatrixDraw()
	print("Initialized")

	start_server = websockets.serve(f.partial(handler, artist = md), "127.0.0.1", 5678)
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

