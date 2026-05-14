import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
    apiKey: "AIzaSyCls3FShbGQ5RqEc2zjDNO0cbfzM5SBJVI",
    authDomain: "agricheck-f90dd.firebaseapp.com",
    projectId: "agricheck-f90dd",
    storageBucket: "agricheck-f90dd.firebasestorage.app",
    messagingSenderId: "503137367705",
    appId: "1:503137367705:web:8df8fba610afc7903d2a08",
    measurementId: "G-BY7C02514X",
};

const app = initializeApp(firebaseConfig);

// Analytics is optional – only available in browser environments
export const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;

export const auth = getAuth(app);
export default app;
