import { api } from '../../source/server.mjs';
export async function onRequest(context) { return api(context.request); }
