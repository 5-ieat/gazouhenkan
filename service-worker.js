// 最低限のPWA認識用おまじない（空っぽでもOKですがイベントだけ登録）
self.addEventListener('fetch', function(event) {
    const urlsToCache = [
    './',              // トップページ（index.htmlを指します）
    './index.html',
    './manifest.json',
    './sub.html',
    './ga.png'

];
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// アクティベート時に古いキャッシュを削除
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// フェッチ要求（ネットワークが繋がらない時はキャッシュを返す）
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
});