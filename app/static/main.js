// Import the functions you need from the SDKs you need
//import { initializeApp } from "firebase/app";
//import { getAnalytics } from "firebase/analytics";
//import { getMessaging, getToken } from "firebase/messaging";
//import { from } from "form-data";

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.17.2/firebase-app.js";
import { getMessaging, getToken, onMessage, deleteToken } from 'https://www.gstatic.com/firebasejs/9.17.2/firebase-messaging.js'

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyA9qSUevps9d7qPlr3n33P9X8B9C97ZfXU",
  authDomain: "flightalert-380817.firebaseapp.com",
  projectId: "flightalert-380817",
  storageBucket: "flightalert-380817.appspot.com",
  messagingSenderId: "958919964394",
  appId: "1:958919964394:web:d1b54a663c4f1a0d918993",
  measurementId: "G-1CMRPTD8HJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
//const analytics = getAnalytics(app);
const messaging = getMessaging(app);

var sw_registration = null

// IDs of divs that display registration token UI or request permission UI.
const tokenDivId = 'token_div';
const permissionDivId = 'permission_div';

// Handle incoming messages. Called when:
// - a message is received while the app has focus
// - the user clicks on an app notification created by a service worker
//   `messaging.onBackgroundMessage` handler.


function resetUI() {
  clearMessages();
  showToken('loading...');
  // Get registration token. Initially this makes a network call, once retrieved
  // subsequent calls to getToken will return from cache.
  getToken(messaging, { vapidKey: 'BBxngHeJQtHsT3PFeRtWbE55QA_3L_pv-HsCoBMF9bPZkCNHf9E9zCcUc742iVzbAIpf7qgYKc-4lu5Xhv7lEfI', serviceWorkerRegistration: sw_registration,}).then((currentToken) => {
    if (currentToken) {
      sendTokenToServer(currentToken);
      updateUIForPushEnabled(currentToken);
    } else {
      // Show permission request.
      console.log('No registration token available. Request permission to generate one.');
      // Show permission UI.
      updateUIForPushPermissionRequired();
      setTokenSentToServer(false);
    }
  }).catch((err) => {
    console.log('An error occurred while retrieving token. ', err);
    showToken('Error retrieving registration token. ', err);
    setTokenSentToServer(false);
    updateUIForPushPermissionRequired();
  });
  (error) => {
    console.error(`Service worker registration failed: ${error}`);
  };

};


function showToken(currentToken) {
  // Show token in console and UI.
  const tokenElement = document.querySelector('#token');
  tokenElement.textContent = currentToken;
};

// Send the registration token your application server, so that it can:
// - send messages back to this app
// - subscribe/unsubscribe the token from topics
function sendTokenToServer(currentToken) {
  //if (!isTokenSentToServer()) {
  if (true) {
    console.log('Sending token to server...');
    // TODO(developer): Send the current token to your server.
    fetch("/postmethod", {
      method: "POST",
      body: JSON.stringify({
        token: currentToken,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    });

    setTokenSentToServer(true);
  } else {
    console.log('Token already sent to server so won\'t send it again ' +
        'unless it changes');
  }
};

function isTokenSentToServer() {
  return window.localStorage.getItem('sentToServer') === '1';
};

function setTokenSentToServer(sent) {
  window.localStorage.setItem('sentToServer', sent ? '1' : '0');
};

function showHideDiv(divId, show) {
  const div = document.querySelector('#' + divId);
  if (show) {
    div.style = 'display: visible';
  } else {
    div.style = 'display: none';
  }
};

function requestPermission() {
  console.log('Requesting permission...');
  Notification.requestPermission().then((permission) => {
    if (permission === 'granted') {
      console.log('Notification permission granted.');
      // TODO(developer): Retrieve a registration token for use with FCM.
      // In many cases once an app has been granted notification permission,
      // it should update its UI reflecting this.
      resetUI();
    } else {
      console.log('Unable to get permission to notify.');
    }
  });
};

function delete_Token() {
  // Delete registration token.
  /*deleteToken(messaging, { vapidKey: 'BBxngHeJQtHsT3PFeRtWbE55QA_3L_pv-HsCoBMF9bPZkCNHf9E9zCcUc742iVzbAIpf7qgYKc-4lu5Xhv7lEfI'}).then(() => {
    console.log('Token deleted.');
    setTokenSentToServer(false);
    // Once token is deleted update UI.
    //resetUI();
  }).catch((err) => {
    console.log('Unable to delete token. ', err);
  });*/
  deleteToken(messaging).then(() => {
    console.log('Token deleted.');
    setTokenSentToServer(false);
  }).catch((err) => {
    console.log('Unable to delete token. ', err);
  });
};

// Add a message to the messages element.
function appendMessage(payload) {
  const messagesElement = document.querySelector('#messages');
  const dataHeaderElement = document.createElement('h5');
  const dataElement = document.createElement('pre');
  dataElement.style = 'overflow-x:hidden;';
  dataHeaderElement.textContent = 'Received message:';
  dataElement.textContent = 'hello'//JSON.stringify(payload, null, 2);
  messagesElement.appendChild(dataHeaderElement);
  messagesElement.appendChild(dataElement);
};

// Clear the messages element of all children.
function clearMessages() {
  const messagesElement = document.querySelector('#messages');
  while (messagesElement.hasChildNodes()) {
    messagesElement.removeChild(messagesElement.lastChild);
  }
};

function updateUIForPushEnabled(currentToken) {
  showHideDiv(tokenDivId, true);
  showHideDiv(permissionDivId, false);
  showToken(currentToken);
};

function updateUIForPushPermissionRequired() {
  showHideDiv(tokenDivId, false);
  showHideDiv(permissionDivId, true);
};

onMessage((payload) => {
  console.log('Message received. ', payload);
  // Update the UI to include the received message.
  appendMessage(payload);
});

window.onload = function() {
  // Add the public key generated from the console here.
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/firebase-messaging-sw.js', { scope: '/' })
    .then((registration) => {
      sw_registration=registration
    });
  }
  resetUI();
  appendMessage("EE")
};

document.getElementById("permission-btn").addEventListener("click", requestPermission); 
document.getElementById("delete-token-btn").addEventListener("click", delete_Token); 