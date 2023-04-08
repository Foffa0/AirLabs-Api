/**
 * Here is is the code snippet to initialize Firebase Messaging in the Service
 * Worker when your app is not hosted on Firebase Hosting.
 // Give the service worker access to Firebase Messaging.
 // Note that you can only use Firebase Messaging here. Other Firebase libraries
 // are not available in the service worker.
 **/
 importScripts('https://www.gstatic.com/firebasejs/9.17.1/firebase-app-compat.js');
 importScripts('https://www.gstatic.com/firebasejs/9.17.1/firebase-messaging-compat.js');
 // Initialize the Firebase app in the service worker by passing in
 // your app's Firebase config object.
 // https://firebase.google.com/docs/web/setup#config-object
 firebase.initializeApp({
  apiKey: "AIzaSyA9qSUevps9d7qPlr3n33P9X8B9C97ZfXU",
  authDomain: "flightalert-380817.firebaseapp.com",
  projectId: "flightalert-380817",
  storageBucket: "flightalert-380817.appspot.com",
  messagingSenderId: "958919964394",
  appId: "1:958919964394:web:d1b54a663c4f1a0d918993",
  measurementId: "G-1CMRPTD8HJ"
 });
 // Retrieve an instance of Firebase Messaging so that it can handle background
 // messages.
 const messaging = firebase.messaging();

// If you would like to customize notifications that are received in the
// background (Web app is closed or not in browser focus) then you should
// implement this optional method.
// Keep in mind that FCM will still show notification messages automatically 
// and you should use data messages for custom notifications.
// For more info see: 
// https://firebase.google.com/docs/cloud-messaging/concept-options
/*messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  // Customize notification here
  const notificationTitle = "payload.notification.title";
  const notificationOptions = {
    body: payload.notification.body,
    image: payload.notification.image,
  };

  self.registration.showNotification(notificationTitle,
    notificationOptions);
});*/