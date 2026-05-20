// 最低限のPWA認識用おまじない（空っぽでもOKですがイベントだけ登録）
self.addEventListener('fetch', function(event) {
    const urlsToCache = [
    './',              // トップページ（index.htmlを指します）
    './index.html',
    './manifest.json',
    './sub.html',
    './ga.ico'

];
});