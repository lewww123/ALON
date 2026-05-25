{% load static %}

const CACHE_NAME = "alon-cache-v1";

const APP_SHELL = [
    "/",
    "/offline/",
    "{% static 'css/style.css' %}",
    "{% static 'manifest.json' %}",
    "{% static 'icons/icon-192x192.png' %}",
    "{% static 'icons/icon-512x512.png' %}"
];

// Install service worker and cache app shell
self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(APP_SHELL);
        })
    );

    self.skipWaiting();
});

// Remove old caches
self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames.map(function (cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );

    self.clients.claim();
});

// Cache strategy
self.addEventListener("fetch", function (event) {
    const request = event.request;
    const url = new URL(request.url);

    // Do not cache uploaded media/audio files because they can be large
    if (url.pathname.startsWith("/media/")) {
        return;
    }

    // For page navigation: network first, then offline page
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(function () {
                return caches.match("/offline/");
            })
        );
        return;
    }

    // For static files: cache first, then network
    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            caches.match(request).then(function (cachedResponse) {
                return cachedResponse || fetch(request).then(function (networkResponse) {
                    return caches.open(CACHE_NAME).then(function (cache) {
                        cache.put(request, networkResponse.clone());
                        return networkResponse;
                    });
                });
            })
        );
    }
});