// Watch what a view of a live site asks of its server, so that capture.js can say it (references/reading-a-live-site.md).
//
// Run it in the page as capture.js is run -- given to the browser's tool that evaluates a function in the page --
// as soon as the view is open, before anything is done in it; where the tool can run a script before every page
// loads, give it this text there, and the view's first calls are seen too. From then on, every call the page
// makes with fetch or XMLHttpRequest is noted: its method, where it went -- the path on the site's own host with
// each ID as {id}, the host and the path on another -- its status, and the shape of its answer where that is JSON:
// the names of its fields and the type of each, `{id: number, status: string, lines: [{amount: number}]}`. Never a
// value, a query, a header, a cookie, a token, or anything the page sends. It makes no request of its own and
// changes nothing the page does: the page gets every answer as it would have. capture.js reads what it noted.
() => {
  "use strict";
  if (window.__specsBuilderWatch) { return "already watching: " + window.__specsBuilderWatch.requests.length + " call(s)"; }
  var noted = [], MOST = 300;

  function template(path) {
    return path.split("/").map(function (part) {
      return /^\d+$|^[0-9a-f]{8}-[0-9a-f]{4}-|^[0-9a-f]{16,}$|^(?=[^/]*\d)[0-9A-Za-z_-]{20,}$/i.test(part) ? "{id}" : part;   // a token holds a digit: get-authenticated-user is a word
    }).join("/");
  }

  function where(address) {
    var url;
    try { url = new URL(address, location.href); } catch (e) { return "(an address it could not read)"; }
    return (url.host === location.host ? "" : url.host) + template(url.pathname);
  }

  function shape(value, depth) {
    if (value === null) { return "null"; }
    if (Array.isArray(value)) { return value.length ? "[" + shape(value[0], depth + 1) + "]" : "[]"; }
    if (typeof value === "object") {
      if (depth > 2) { return "{…}"; }
      var keys = Object.keys(value);
      return "{" + keys.slice(0, 16).map(function (key) {
        return (/^\d+$|^[0-9a-f-]{16,}$/i.test(key) ? "{id}" : key) + ": " + shape(value[key], depth + 1);
      }).join(", ") + (keys.length > 16 ? ", …" : "") + "}";
    }
    return typeof value;
  }

  function note(kind, method, address, status, body) {
    if (noted.length >= MOST) { return; }
    var said = body === undefined ? "" : shape(body, 0);
    var call = { kind: kind, method: String(method || "GET").toUpperCase(), where: where(address), status: status,
                 shape: said.length > 300 ? said.slice(0, 297) + "..." : said };
    var same = noted.some(function (other) {
      return other.method === call.method && other.where === call.where && other.status === call.status &&
             other.shape === call.shape;
    });
    if (!same) { noted.push(call); }
  }

  var fetched = window.fetch;
  if (fetched) {
    window.fetch = function (input, init) {
      var method = (init && init.method) || (input && input.method) || "GET";
      var address = typeof input === "string" ? input : input && input.url ? input.url : String(input);
      return fetched.apply(this, arguments).then(function (answer) {
        try {
          var type = answer.headers.get("content-type") || "";
          if (type.indexOf("json") >= 0) {
            answer.clone().json().then(function (body) { note("fetch", method, address, answer.status, body); },
                                       function () { note("fetch", method, address, answer.status); });
          } else {
            note("fetch", method, address, answer.status);
          }
        } catch (e) { note("fetch", method, address, answer.status); }
        return answer;
      }, function (problem) {
        note("fetch", method, address, 0);
        throw problem;
      });
    };
  }

  var opened = XMLHttpRequest.prototype.open, sent = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, address) {
    this.__specsBuilder = { method: method, address: address };
    return opened.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function () {
    var request = this, asked = request.__specsBuilder;
    if (asked) {
      request.addEventListener("loadend", function () {
        var body;
        try {
          var type = request.getResponseHeader("content-type") || "";
          if (request.responseType === "json") { body = request.response; }
          else if (type.indexOf("json") >= 0 && (request.responseType === "" || request.responseType === "text")) {
            body = JSON.parse(request.responseText);
          }
        } catch (e) { body = undefined; }
        note("xmlhttprequest", asked.method, asked.address, request.status, body);
      });
    }
    return sent.apply(this, arguments);
  };

  window.__specsBuilderWatch = { requests: noted };
  return "watching";
}
