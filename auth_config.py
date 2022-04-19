import pyrebase
from datetime import datetime

def firebase_instances():

    firebaseConfig = {
                    'apiKey': "AIzaSyDGpmk98MxSnuZKuk0gwHhU65I-AZbRZGw",
                    'authDomain': "endometrics.firebaseapp.com",
                    'projectId': "endometrics",
                    'databaseURL': 'https://endometrics-default-rtdb.firebaseio.com',
                    'storageBucket': "endometrics.appspot.com",
                    'messagingSenderId': "476045102168",
                    'appId': "1:476045102168:web:61e32209661245d30b4e2d",
                    'measurementId': "G-MEW8B7KZY5"
                    }

    #firebase auth
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()

    #storage
    db = firebase.database()
    storage = firebase.storage()

    return auth, db, storage