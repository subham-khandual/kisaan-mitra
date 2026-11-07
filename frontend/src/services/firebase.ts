import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDh7elFGbhw6VJUv5H_WjfQz6tohN13Ljg",
  authDomain: "farming-b0758.firebaseapp.com",
  projectId: "farming-b0758",
  storageBucket: "farming-b0758.firebasestorage.app",
  messagingSenderId: "864232130665",
  appId: "1:864232130665:web:d6d9f73c44b82577d5faf8",
  measurementId: "G-1NQBSE8NCJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
