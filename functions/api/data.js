const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxLhWmSBgvuB_UxKx1ZxoDhFBjP-tqxSqdpGlWrcOpXJExRbigyqb1vFlamxBO38EXyLw/exec';
const CACHE_TTL = 3600;

export async function onRequest(context) {
  const cache = caches.default;
  const cacheKey = new Request('https://cache.dashboard-teatro.pages.dev/api/data', { method: 'GET' });

  let response = await cache.match(cacheKey);
  if (response) {
    const headers = new Headers(response.headers);
    headers.set('X-Cache', 'HIT');
    return new Response(response.body, { status: 200, headers });
  }

  const origin = await fetch(APPS_SCRIPT_URL, { redirect: 'follow' });
  if (!origin.ok) {
    return new Response(JSON.stringify({ error: 'upstream_error', status: origin.status }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }

  const body = await origin.text();
  response = new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': `public, max-age=${CACHE_TTL}`,
      'Access-Control-Allow-Origin': '*',
      'X-Cache': 'MISS'
    }
  });

  context.waitUntil(cache.put(cacheKey, response.clone()));
  return response;
}
