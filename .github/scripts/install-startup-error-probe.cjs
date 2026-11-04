const fs = require('node:fs');
const path = 'dist/index.html';
const html = fs.readFileSync(path, 'utf8');
const probe = `<script>
function showSmokeError(message) {
  const output = document.createElement('pre');
  output.style.cssText = 'position:fixed;z-index:999999;top:35px;left:10px;right:10px;background:white;color:black;white-space:pre-wrap';
  output.textContent = String(message);
  document.body.append(output);
}
window.addEventListener('error', event => showSmokeError(event.message || 'Resource failed: ' + event.target.src), true);
window.addEventListener('unhandledrejection', event => showSmokeError(event.reason?.stack || event.reason));
</script>`;
fs.writeFileSync(path, html.replace('<head>', '<head>' + probe));
