import { api } from '../source/server.mjs';
export default {
  async fetch(request, env) {
    return new URL(request.url).pathname.startsWith('/api/')
      ? api(request)
      : env.ASSETS.fetch(request);
  }
};
