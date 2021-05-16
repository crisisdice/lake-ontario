function load_svg() {
	fetch(new URL("/lake.svg", location.origin))
		.then(response => response.text())
		.then(text => {
			document.getElementById("container").innerHTML = text;
		});
}

function handle_click(event) {
	const id = event.path[0]?.id;

	if (id === null || isNaN(parseInt(id)))
		return;

	if (ws?.readyState == WebSocket.OPEN)
		ws.close()

	const request = {
		node: parseInt(id),
		season: document.getElementById("season").value,
	};

	ws = connect(request);
}

function connect(request) {
	const ws = new WebSocket(`ws://${location.host}/websocket`);

	ws.onopen = function() {
		ws.send(JSON.stringify(request));
	};

	ws.onmessage = function(message) {
		let body = JSON.parse(message.data);
		reset_lake();
		color_lake(body.nodes);
	};

	ws.onclose = function() {
		console.warn("Connection closed");
	}

	return ws;
}

function reset_lake() {
	const lake = Array.prototype.slice.call(document.getElementById("lake").children);
	lake.forEach(water => {
		water.style.fill = "rgb(247, 252, 253)";
	});
}

function color_lake(nodes) {
	nodes.forEach(node => {
		const water = document.getElementById(node.id);
		water.style.fill = node.color;
	});
}
