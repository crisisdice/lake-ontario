var fs = require('fs');
var readline = require('readline');
var math = require('mathjs');

async function processLineByLine() {
  const fileStream = fs.createReadStream('data');

  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });

  let array = [];

  for await (const line of rl) {
	 array.push(line)
  }
  return array;
}

console.log("starting");

processLineByLine().then(lines =>
{
	processMatrix(lines);
}).catch(err => {
	console.log(err)
});

function processMatrix(lines)
{
	console.log("imported");

	let matrix = [];

	for (i=0; i < lines.length; i ++)
	{
		let row = lines[i];

		let split = row.split("   ");

		let map = split.filter(x => x.length > 0);

		let parse = map.map(x => parseFloat(x));

		matrix.push(parse);
	}

	
	let matrix_cast = math.matrix(matrix);

	console.log("multiplying");


	let square = math.square(matrix_cast);

	console.log("done");
}
