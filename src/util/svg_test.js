function get_M(element) {
	let d = element.getAttribute("d").split(" ");
	return `${d[1]} ${d[2]}`;
}

function get_L(element) {
	let d = element.getAttribute("d").split(" ");
	return `${d[5]} ${d[6]}`;
}

function test() {
	let a = document.getElementById("PolyCollection_1");
	let nodes = Array.prototype.slice.call(a.children);
	
	nodes.forEach((x, i) => {
		let m = get_L(x)
		let l = get_M(nodes[i + 1])
		
		if (m != l)
			x.style.fill = "rgb(0, 0, 0)"
	});
}