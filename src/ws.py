import asyncio
import websockets

async def process(websocket, path):
	args = await websocket.recv()
	print(args)

	f = open("t.svg", "r")

	graphic = f.read()
	await websocket.send(graphic)

start_server = websockets.serve(process, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
