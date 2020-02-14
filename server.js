/* eslint-env node */
const http = require('http');

const requestListener = function (req, res) {
  if (req.url === '/get-players') {
    res.writeHead(200);
    res.end(JSON.stringify([
      { id: 0, name: 'SkyNet', code: '() => Math.floor(Math.random() * 6)' },
      { id: 1, name: 'HAL 9000', code: '() => Math.floor(Math.random() * 6)' },
    ]));
    return;
  }
  let data = '';
  req.on('data', chunk => data += chunk);
  req.on('end', () => console.log(data));
  res.writeHead(200);
  res.end('Hello, World!');
}

const server = http.createServer(requestListener);
server.listen(8080);
