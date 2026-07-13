const securityHeaders = {
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
};

async function serve(request, env) {
  if (!env?.ASSETS?.fetch) {
    return new Response("Static assets are unavailable.", { status: 503 });
  }

  if (!new Set(["GET", "HEAD"]).has(request.method)) {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { Allow: "GET, HEAD" },
    });
  }

  const url = new URL(request.url);
  const firstAssetUrl = new URL(url);
  if (firstAssetUrl.pathname === "/") firstAssetUrl.pathname = "/index.html";

  let response = await env.ASSETS.fetch(new Request(firstAssetUrl, request));
  const acceptsHtml = request.headers.get("Accept")?.includes("text/html");
  if (response.status === 404 && acceptsHtml) {
    response = await env.ASSETS.fetch(new Request(new URL("/index.html", request.url), request));
  }

  const headers = new Headers(response.headers);
  for (const [name, value] of Object.entries(securityHeaders)) headers.set(name, value);
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export default { fetch: serve };
export { serve as fetch };
