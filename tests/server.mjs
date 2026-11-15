import assert from 'node:assert/strict';
import { api } from '../source/server.mjs';
import handler, { config } from '../netlify/functions/mesora.mjs';
import { onRequest } from '../functions/api/[[path]].js';
import worker from '../worker/index.mjs';
for (const fn of [api, handler, request => onRequest({request})]) {
  assert.equal((await fn(new Request('https://mesora.example/api/power?lat=999&lon=0'))).status, 400);
  assert.equal((await fn(new Request('https://mesora.example/api/water-results?site=bad%20input'))).status, 400);
}
assert.equal(config.path, '/api/*');
assert.equal((await worker.fetch(new Request('https://mesora.example/api/unknown'),{})).status,404);
const response=await worker.fetch(new Request('https://mesora.example/'),{ASSETS:{fetch:async()=>new Response('static asset')}});
assert.equal(await response.text(),'static asset');
console.log('PASS: portable hosting adapters, invalid inputs, and static asset routing.');
const {default:vercel}=await import('../api/data.mjs');
const output={headers:{},setHeader(k,v){this.headers[k]=v;},end(body){this.body=body;}};
await vercel({url:'/api/data?endpoint=power&lat=999&lon=0',method:'GET'},output);
assert.equal(output.statusCode,400);
assert.equal(JSON.parse(output.body).error,'Invalid coordinates');
assert.equal(output.headers['access-control-allow-origin'],'*');
console.log('PASS: Vercel rewrite, JSON errors, and cross-origin public data access.');
