// Minimal Node server to serve the JS-only SPA
// Run: node server.js, then open http://localhost:3000

const http = require('http');
const path = require('path');
const fs = require('fs');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

const mime = {
  '.js': 'text/javascript; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  'default': 'text/plain; charset=utf-8',
};

function indexHtml() {
  return `<!doctype html>
  <html lang="ko">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>빙고루트 | BingoRoute</title>
      <meta name="description" content="서울을 더 스마트하게 여행하세요" />
      <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='16' fill='%230055FF'/%3E%3Ctext x='16' y='21' font-size='16' text-anchor='middle' fill='white' font-family='Arial, Helvetica, sans-serif'%3EB%3C/text%3E%3C/svg%3E" />
      <script type="module" src="/public/main.js"></script>
    </head>
    <body>
      <div id="app">로딩중…</div>
    </body>
  </html>`;
}

const server = http.createServer((req, res) => {
  // Root serves the SPA shell
  if (req.url === '/' || req.url.startsWith('/#')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(indexHtml());
    return;
  }

  // Serve files under /public
  if (req.url.startsWith('/public/')) {
    const filePath = path.join(__dirname, req.url);
    if (!filePath.startsWith(PUBLIC_DIR)) {
      res.writeHead(403);
      return res.end('Forbidden');
    }
    fs.readFile(filePath, (err, buf) => {
      if (err) {
        res.writeHead(404);
        return res.end('Not found');
      }
      const ext = path.extname(filePath);
      res.writeHead(200, { 'Content-Type': mime[ext] || mime.default });
      res.end(buf);
    });
    return;
  }

  res.writeHead(302, { Location: '/' });
  res.end();
});

server.listen(PORT, () => {
  console.log(`BingoRoute running at http://localhost:${PORT}`);
});

