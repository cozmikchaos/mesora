import { api } from '../../source/server.mjs';
export default async function handler(request) { return api(request); }
export const config = { path: '/api/*' };
