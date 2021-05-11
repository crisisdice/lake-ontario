let ws = null;

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
		let lat = -75.847104 - ((863 - x) * 0.00572);
		let lng = 42.964627 + ((683 - y) * 0.00253);

		console.info(`Sending x: ${lat} y: ${lng} to server`);

		const obj = { 
			lat: lat,
			lng: lng
		};

		ws.send(JSON.stringify(obj));
	};

  	ws.onmessage = function(event) {
		var anchor = document.getElementById("container");
		anchor.innerHTML = event.data;
	};

	ws.onclose = function() {
		console.warn("Connection closed");
	}

	return ws;
}
