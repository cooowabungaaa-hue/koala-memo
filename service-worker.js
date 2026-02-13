const CACHE_NAME = 'koala-memo-v2';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  // アイコン画像があればここに追加
  // './icon.png'
];

// インストール時にキャッシュする
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function (cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// 新しいサービスワーカーがアクティブになったときに古いキャッシュを削除する
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames.filter(function (cacheName) {
          return cacheName !== CACHE_NAME;
        }).map(function (cacheName) {
          return caches.delete(cacheName);
        })
      );
    })
  );
});

// リクエスト時にキャッシュがあれば返し、なければネットワークから取得する
self.addEventListener('fetch', function (event) {
  event.respondWith(
    caches.match(event.request)
      .then(function (response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});