setTimeout(function () {
  $("#message").fadeOut("slow");
}, 5000);

var words = [
    "Extensive Job Opportunities",
    "Time and Effort Savings",
    "Enhanced Visibility",
    "Convenient Application Management",
    "Career Guidance and Resources",
    "Discover the best job opportunities tailored for you.",
  ],
  part,
  i = 0,
  offset = 0,
  len = words.length,
  forwards = true,
  skip_count = 0,
  skip_delay = 40,
  speed = 160;
var wordflick = function () {
  setInterval(function () {
    if (forwards) {
      if (offset >= words[i].length) {
        ++skip_count;
        if (skip_count == skip_delay) {
          forwards = false;
          skip_count = 0;
        }
      }
    } else {
      if (offset == 0) {
        forwards = true;
        i++;
        offset = 0;
        if (i >= len) {
          i = 0;
        }
      }
    }
    part = words[i].substr(0, offset);
    if (skip_count == 0) {
      if (forwards) {
        offset++;
      } else {
        offset--;
      }
    }
    $(".word").text(part);
  }, speed);
};

$(document).ready(function () {
  wordflick();
});

// Function to update the notifications count
function updateNotificationsCount() {
  fetch("/notifications-count/")
    .then((response) => response.json())
    .then((data) => {
      // Update the notifications count element with the received data
      document.getElementById("notifications-count").textContent = data.count;
    })
    .catch((error) => console.log("Error:", error));
}

// Each WebSocket push represents exactly one newly-created notification,
// so bump the displayed count directly instead of re-fetching it over HTTP.
function incrementNotificationsCount() {
  const el = document.getElementById("notifications-count");
  if (!el) {
    return;
  }
  const current = parseInt(el.textContent, 10) || 0;
  el.textContent = current + 1;
}

// Real-time notifications + chat: one WebSocket per browser tab, not one
// per page. hx-boost (see navbar.html/base.html) swaps <body>'s innerHTML
// on every navigation, which includes this <script src="main.js"> tag -
// htmx re-executes swapped <script> tags by default, so this whole file
// re-runs on every single boosted navigation, not just once. Anything
// stored in a page-local variable (including a WebSocket instance) is lost
// on the very next boosted nav; the socket itself was never closed, so
// naively "open a socket if none exists" instead opens a new one every
// time and leaks the old ones - each still-open connection then delivers
// its own copy of every push, multiplying the displayed notification count
// by however many sockets have piled up. window survives boosted swaps
// (only the DOM is replaced, not the JS heap), so the single live socket -
// and any pending reconnect timer - are tracked there instead, and this
// function is idempotent: called again with the same target, it's a no-op.
function ensureRealtimeSocket(applicationId) {
  applicationId = applicationId || null;

  // The connected target is tracked on the socket object itself
  // (__applicationId below), not on a shared window variable - a page's
  // own inline script also writes window.__realtimeApplicationId (as a
  // declarative "what this page wants", read as this function's fallback
  // argument), and comparing against that same variable here would let
  // the caller's own assignment silently corrupt this check: it could
  // make an existing socket connected to the WRONG target look
  // already-correct, simply because the caller had just overwritten the
  // shared marker to match before calling in.
  const alreadyConnecting =
    window.__realtimeSocket &&
    window.__realtimeSocket.__applicationId === applicationId &&
    (window.__realtimeSocket.readyState === WebSocket.OPEN ||
      window.__realtimeSocket.readyState === WebSocket.CONNECTING);
  if (alreadyConnecting) {
    return;
  }

  if (window.__realtimeReconnectTimer) {
    clearTimeout(window.__realtimeReconnectTimer);
    window.__realtimeReconnectTimer = null;
  }
  if (window.__realtimeSocket) {
    // Detach onclose first - otherwise closing this stale socket would
    // trigger its own reconnect-on-close below, racing the new one.
    window.__realtimeSocket.onclose = null;
    window.__realtimeSocket.close();
  }

  const wsScheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  const url =
    wsScheme +
    "//" +
    window.location.host +
    "/ws/updates/" +
    (applicationId ? applicationId + "/" : "");

  function connect() {
    const socket = new WebSocket(url);
    socket.__applicationId = applicationId;
    window.__realtimeSocket = socket;

    socket.onmessage = function (event) {
      const data = JSON.parse(event.data);
      if (data.kind === "notification") {
        // Each push is exactly one new notification - increment locally
        // instead of re-fetching the count over HTTP.
        incrementNotificationsCount();
      } else if (data.kind === "chat" && window.__onRealtimeChatMessage) {
        window.__onRealtimeChatMessage(data);
      }
    };

    socket.onerror = function (error) {
      console.log("Realtime socket error:", error);
    };

    // The connection can be dropped by the server (e.g. an idle timeout on
    // its channel-layer backend) even while this tab stays open, so it
    // must reconnect on its own rather than assume one connect() is enough.
    // Guarded by identity: a socket intentionally replaced by a newer
    // ensureRealtimeSocket() call (e.g. navigating to a different
    // application's chat) must not also schedule a reconnect for itself.
    socket.onclose = function () {
      if (window.__realtimeSocket === socket) {
        window.__realtimeReconnectTimer = setTimeout(connect, 3000);
      }
    };
  }

  connect();
}

// Only when the notifications UI is present (i.e. the user is authenticated).
if (document.getElementById("notifications-count")) {
  updateNotificationsCount(); // initial render, before any socket delivers anything
  ensureRealtimeSocket(window.__realtimeApplicationId);
}

// htmx re-executing this script on every boosted swap (see above) would
// also re-register this listener additively, firing it multiple times per
// navigation - guard with a flag on document.body, which (like window)
// survives the swap.
if (!document.body.__realtimeListenersBound) {
  document.body.__realtimeListenersBound = true;

  // hx-boost swaps the navbar's DOM on every navigation (fresh, empty
  // #notifications-count node) - and visiting the notifications page marks
  // notifications as seen server-side, which the locally-incremented count
  // never learns about on its own. Re-fetch the true count after every
  // boosted swap so it can't drift from the server.
  document.body.addEventListener("htmx:afterSettle", () => {
    if (document.getElementById("notifications-count")) {
      updateNotificationsCount();
    }
  });

  document.body.addEventListener("htmx:configRequest", (event) => {
    event.detail.headers["X-CSRFToken"] = "{{ csrf_token }}";
  });
}
