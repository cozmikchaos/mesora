import { api } from '../../source/server.mjs';
export default async function handler(request) {const url=new URL(request.url);if(url.pathname.startsWith('/.netlify/functions/mesora/'))url.pathname='/api/'+url.pathname.split('/').at(-1);return api(new Request(url,request));}
export const config = { path:'/api/*' };
