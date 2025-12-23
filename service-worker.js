const CACHE_NAME = 'koala-memo-v1';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  // アイコン画像があればここに追加
  // './icon.png'
];

// インストール時にキャッシュする
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// リクエスト時にキャッシュを返す
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});