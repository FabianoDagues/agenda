const CACHE='agenda-family-v2';
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(['/static/style.css','/static/app.js','/static/icon-192.png'])));self.skipWaiting()});
self.addEventListener('activate',event=>{event.waitUntil(self.clients.claim())});
self.addEventListener('push',event=>{let payload={title:'Lembrete da agenda',body:'Você tem um compromisso.',url:'/'};try{payload={...payload,...event.data.json()}}catch(e){}event.waitUntil(self.registration.showNotification(payload.title,{body:payload.body,icon:'/static/icon-192.png',badge:'/static/icon-192.png',data:{url:payload.url}}))});
self.addEventListener('notificationclick',event=>{event.notification.close();event.waitUntil(self.clients.openWindow(event.notification.data?.url||'/'))});
