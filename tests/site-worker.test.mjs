import assert from "node:assert/strict";
import test from "node:test";

import worker from "../sites/server/index.js";

test("Sites worker serves static assets with security headers", async () => {
  const requestedPaths = [];
  const response = await worker.fetch(
    new Request("https://example.com/"),
    {
      ASSETS: {
        fetch: async (request) => {
          requestedPaths.push(new URL(request.url).pathname);
          return new Response("home", { status: 200 });
        },
      },
    },
  );

  assert.equal(response.status, 200);
  assert.equal(await response.text(), "home");
  assert.deepEqual(requestedPaths, ["/index.html"]);
  assert.equal(response.headers.get("X-Content-Type-Options"), "nosniff");
  assert.equal(response.headers.get("X-Frame-Options"), "DENY");
});

test("Sites worker rejects writes", async () => {
  const response = await worker.fetch(
    new Request("https://example.com/", { method: "POST" }),
    { ASSETS: { fetch: async () => new Response("unused") } },
  );

  assert.equal(response.status, 405);
  assert.equal(response.headers.get("Allow"), "GET, HEAD");
});
