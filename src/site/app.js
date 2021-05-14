let ws = null;

load_svg();

async function load_svg() {
	let anchor = document.getElementById("container");

	let url = new URL("http://localhost:8000/slake.svg");
	let f = await fetch(url);
	let s = await f.text();

	anchor.innerHTML = s;
}

function handle_click(e) {
	let x = e.offsetX;
	let y = e.offsetY;

	if (!validate_coords(x, y))
		return;

	if (ws?.readyState == WebSocket.OPEN)
		ws.close();

	ws = get_ws(x, y);
}

function validate_coords(x, y) {
	return (118 < x && x < 864) && (91 < y && y < 684);
}

function get_ws(x, y) {
	let ws = new WebSocket("ws://127.0.0.1:5678/");

	ws.onopen = function() {
		let lng = -75.847104 - ((863 - x) * 0.00572);
		let lat = 42.964627 + ((683 - y) * 0.00253);

		console.info(`Sending x: ${lng} y: ${lat} to server`);

		const obj = { 
			lat: lat,
			lng: lng,
			season: document.getElementById("season"),
			id: uuid()
		};

		ws.send(JSON.stringify(obj));
	};

  	ws.onmessage = function(event) {
		let anchor = document.getElementById("container");
		anchor.innerHTML = event.data;
	};

	ws.onclose = function() {
		console.warn("Connection closed");
	}

	return ws;
}

function uuid() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}
