/* eslint-env node */
const http = require('http');

const requestListener = function (req, res) {
  let data = '';
  req.on('data', chunk => data += chunk);
  req.on('end', () => console.log(data));
  res.writeHead(200);
  res.end('Hello, World!');
}

const server = http.createServer(requestListener);
server.listen(8080);
