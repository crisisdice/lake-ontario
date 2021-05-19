let ws = null;

function load_svg() {
	fetch(new URL("/lake.svg", location.origin))
		.then(response => response.text())
		.then(text => {
			document.getElementById("display").innerHTML = text;
		});
}

function handle_click(event) {
	let target = event.target;
	let id = target?.id;

	if (id === null || isNaN(parseInt(id)))
		return;

	if (ws?.readyState == WebSocket.OPEN)
		ws.close();

	reset_lake();
	update_title(0);
	target.style.fill = "rgb(0, 0, 0)";

	const request = {
		node: parseInt(id),
		season: "fall", //document.getElementById("season").value,
		intensity: parseInt(document.getElementById("intensity").value)
	};

	ws = connect(request);
}

function connect(request) {
	const ws = new WebSocket(`ws://${location.host}/websocket`);
	let counter = 0;

	ws.onopen = function() {
		ws.send(JSON.stringify(request));
	};

	ws.onmessage = function(message) {
		let body = JSON.parse(message.data);
		reset_lake();
		color_lake(body.nodes);
		counter += 1;
		update_title(counter);
	};

	ws.onclose = function() {
		console.warn("Connection closed");
	}

	return ws;
}

function reset_lake() {
	const lake = Array.prototype.slice.call(document.getElementById("lake").children);
	lake.forEach(water => {
		water.style.fill = "rgb(12, 7, 134)";
	});
}

function color_lake(nodes) {
	nodes.forEach(node => {
		const water = document.getElementById(node.id);
		water.style.fill = node.color;
	});
}

function update_title(counter) {
	let title = "Lake Ontario";

	if (counter > 0)
		title = `${title} - ${counter * 2} days`;

	document.getElementById("title").innerHTML = title;
}
