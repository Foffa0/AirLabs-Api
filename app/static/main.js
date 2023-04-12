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
const deleteTokenDivId = 'delete-token_div';
const permissionDivId = 'permission_div';
const requestTokenDivId = 'request-token_div'

// Handle incoming messages. Called when:
// - a message is received while the app has focus
// - the user clicks on an app notification created by a service worker
//   `messaging.onBackgroundMessage` handler.


function resetUI() {
  clearMessages();
  //showToken('loading...');
  // Get registration token. Initially this makes a network call, once retrieved
  // subsequent calls to getToken will return from cache.
  if (isTokenSentToServer()) {
    getToken(messaging, { vapidKey: 'BBxngHeJQtHsT3PFeRtWbE55QA_3L_pv-HsCoBMF9bPZkCNHf9E9zCcUc742iVzbAIpf7qgYKc-4lu5Xhv7lEfI', serviceWorkerRegistration: sw_registration,}).then((currentToken) => {
      if (currentToken) {
        sendTokenToServer(currentToken);
        updateUIForPushEnabled();
        setLastToken(currentToken);
      } else {
        // Show permission request.
        console.log('No registration token available. Request permission to generate one.');
        // Show permission UI.
        updateUIForPushPermissionRequired();
        setTokenSentToServer(false);
      }
    }).catch((err) => {
      console.log('An error occurred while retrieving token. ', err);
      //showToken('Error retrieving registration token. ', err);
      setTokenSentToServer(false);
      updateUIForPushPermissionRequired();
    });
  } else {
    updateUIForPushDisabled();
  }
};

function subscribeDevice() {
  getToken(messaging, { vapidKey: 'BBxngHeJQtHsT3PFeRtWbE55QA_3L_pv-HsCoBMF9bPZkCNHf9E9zCcUc742iVzbAIpf7qgYKc-4lu5Xhv7lEfI', serviceWorkerRegistration: sw_registration,}).then((currentToken) => {
    if (currentToken) {
      sendTokenToServer(currentToken);
      updateUIForPushEnabled();
      setLastToken(currentToken);
    } else {
      // Show permission request.
      console.log('No registration token available. Request permission to generate one.');
      // Show permission UI.
      updateUIForPushPermissionRequired();
      setTokenSentToServer(false);
    }
  }).catch((err) => {
    console.log('An error occurred while retrieving token. ', err);
    //showToken('Error retrieving registration token. ', err);
    setTokenSentToServer(false);
    updateUIForPushPermissionRequired();
  });
}

// Send the registration token your application server, so that it can:
// - send messages back to this app
// - subscribe/unsubscribe the token from topics
function sendTokenToServer(currentToken) {
  if (!isTokenSentToServer() || !compareWithLastToken(currentToken)) {
    if (!window.localStorage.getItem('last_Token') === null) {
      delete_Token(window.localStorage.getItem('last_Token'));
    }
    console.log('Sending token to server...');
    //Send the current token to your server.
    fetch("/add-token", {
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

function setLastToken(token) {
  window.localStorage.setItem('last_Token', String(token));
};

function compareWithLastToken(token) {
  return window.localStorage.getItem('last_Token') === token;
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

function delete_Token(token=null) {
  console.log(token)
  if (token != null) {
    console.log("token: " + token)
    fetch("/remove-token", {
      method: "POST",
      body: JSON.stringify({
        token: token,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    });
  } else {
    getToken(messaging, { vapidKey: 'BBxngHeJQtHsT3PFeRtWbE55QA_3L_pv-HsCoBMF9bPZkCNHf9E9zCcUc742iVzbAIpf7qgYKc-4lu5Xhv7lEfI', serviceWorkerRegistration: sw_registration,}).then((currentToken) => {
      deleteToken(messaging).then(() => {
        console.log('Token deleted.');
        fetch("/remove-token", {
          method: "POST",
          body: JSON.stringify({
            token: currentToken,
          }),
          headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
        });
        setTokenSentToServer(false);
        updateUIForPushDisabled()
      }).catch((err) => {
        console.log('Unable to delete token. ', err);
      });
    }).catch((err) => {
      console.log('An error occurred while retrieving token. ', err);
      //showToken('Error retrieving registration token. ', err);
      setTokenSentToServer(false);
      updateUIForPushPermissionRequired();
    });
  };
};

// Add a message to the messages element.
function appendMessage(payload) {
  const messagesElement = document.querySelector('#messages');
  const dataHeaderElement = document.createElement('h5');
  const dataElement = document.createElement('pre');
  dataElement.style = 'overflow-x:hidden;';
  dataHeaderElement.textContent = 'New Alert!';
  dataElement.textContent = payload.notification.body;
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

function updateUIForPushEnabled() {
  showHideDiv(deleteTokenDivId, true);
  showHideDiv(permissionDivId, false);
  showHideDiv(requestTokenDivId, false)
  //showToken(currentToken);
};

function updateUIForPushDisabled() {
  showHideDiv(deleteTokenDivId, false);
  showHideDiv(permissionDivId, false);
  showHideDiv(requestTokenDivId, true)
  //showToken(currentToken);
};

function updateUIForPushPermissionRequired() {
  showHideDiv(deleteTokenDivId, false);
  showHideDiv(permissionDivId, true);
};
/*
onMessage((payload) => {
  console.log('Message received. ', payload);
  // Update the UI to include the received message.
  appendMessage(payload);
});*/
onMessage(messaging, (payload) => {
  console.log('Message received. ', payload);
  appendMessage(payload)
});

window.onload = function() {
  // Add the public key generated from the console here.
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/firebase-messaging-sw.js', { scope: '/' })
    .then((registration) => {
      sw_registration=registration
    },
    (error) => {
      console.error(`Service worker registration failed: ${error}`);
    });
    
  }
  resetUI();
};

document.getElementById("permission-btn").addEventListener("click", requestPermission); 
document.getElementById("delete-token-btn").addEventListener("click", function(){
  delete_Token(null);
}); 
document.getElementById("request-token-btn").addEventListener("click", subscribeDevice); 