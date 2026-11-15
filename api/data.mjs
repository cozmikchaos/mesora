import { api } from '../source/server.mjs';
export default async function handler(req, res) {
  const url = new URL(req.url, 'https://mesora.example');
  const endpoint = url.searchParams.get('endpoint');
  if (endpoint) {
    if (!/^[a-z-]{1,30}$/.test(endpoint)) { res.statusCode=400;res.end('Invalid endpoint');return; }
    url.pathname='/api/'+endpoint;
    url.searchParams.delete('endpoint');
  }
  const response = await api(new Request(url, { method:req.method||'GET' }));
  res.statusCode=response.status;
  for (const [key,value] of response.headers) res.setHeader(key,value);
  res.end(Buffer.from(await response.arrayBuffer()));
}
