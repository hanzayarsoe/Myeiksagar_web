import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getFirestore,
  collection,
  addDoc,
  doc,
  setDoc,
  getDoc,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";
// TODO: Add SDKs for Firebase products that you want to use

const firebaseConfig = {
  apiKey: "AIzaSyDXqUme6SVWB4g9q15AtC9xz7aXavYEzLE",
  authDomain: "myeiksagar-c1009.firebaseapp.com",
  databaseURL: "https://myeiksagar-c1009-default-rtdb.firebaseio.com",
  projectId: "myeiksagar-c1009",
  storageBucket: "myeiksagar-c1009.appspot.com",
  messagingSenderId: "854716496772",
  appId: "1:854716496772:web:6318d517660fe012603bd1",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

const db = getFirestore(app);

var myanmar = document.getElementById("Myanmar");
var myeik = document.getElementById("Myeik");
var translate = document.getElementById("translate");
var dropdown = document.getElementById("dropdown");

var translateBtn = document.getElementById("translateBtn");
var clearBtn = document.getElementById("clearBtn");
var segmentBtn = document.getElementById("segmentBtn");

function clearFields() {
  myanmar.value = "";
  myeik.value = "";
  translate.value = "";
  console.log("Cleared Successfully");
}

async function translateText() {
  var myanmarText = myanmar.value;

  // Check if myanmarText is not empty before proceeding
  if (myanmarText.trim() !== "") {
    // Use getDoc to retrieve a document by its ID
    myanmarText = myanmarText.replace(/\s/g, "");
    const docRef = doc(db, "data", myanmarText);
    const docSnapshot = await getDoc(docRef);

    if (docSnapshot.exists()) {
      // Display the value in myeikText
      myeik.value = docSnapshot.data().value;
      console.log("Document found with ID: ", myanmarText);
    } else {
      console.log("Document not found with ID: ", myanmarText);
      alert(myanmarText + "   ဆိုသည့် စကားလုံးကို ရှာမတွေ့ပါ");
    }
  } else {
    console.error("myanmarText is empty. Please provide a non-empty value.");
    alert(" ကျေးဇူးပြု၍ ပြောင်းလိုသော စားလုံးကိုရေးပေးပါ");
  }
}

const myConsonant = "\u1000-\u1021"; // "က-အ"

const enChar = "a-zA-Z0-9";

// "ဣဤဥဦဧဩဪဿ၌၍၏၀-၉၊။!-/:-@[-`{-~\s"
const otherChar =
  "\u1023\u1024\u1025\u1026\u1027\u1029\u102a\u103f\u104c\u104d\u104f\u1040-\u1049\u104a\u104b!-/:-@\\[-`\\{-~\\s";

const ssSymbol = "\u1039";

const ngaThat = "\u1004\u103a";

const aThat = "\u103a";

// Regular expression pattern for Myanmar syllable breaking
// *** a consonant not after a subscript symbol AND a consonant is not
// followed by a-That character or a subscript symbol
const BREAK_PATTERN = new RegExp(
  `((?!${ssSymbol})[${myConsonant}](?![${aThat}${ssSymbol}])|[${enChar}${otherChar}])`,
  "mg"
);

function segment(text) {
  var outArray = text.replace(BREAK_PATTERN, "𝕊$1").split("𝕊");
  if (outArray.length > 0) {
    outArray.shift();
    //out.splice(0, 1);
  }
  return outArray;
}

const BREAK_PATTERN_CHAR = new RegExp(
  `((?!${ssSymbol})[${myConsonant}](?![${aThat}${ssSymbol}])|[${enChar}${otherChar}])`,
  "mg"
);

function segmentWord(text) {
  var outArray = text.split("");
  return outArray;
}

clearBtn.addEventListener("click", clearFields);
translateBtn.addEventListener("click", translateText);
segmentBtn.addEventListener("click", () => {
  var selectedMode = dropdown.value;
  if (selectedMode === "syllabus") {
    var resultvalue = segment(myeik.value);
    translate.value = resultvalue.join(" | ");
  } else if (selectedMode === "character") {
    var resultvalue = segmentWord(myeik.value);
    translate.value = resultvalue.join(" | ");
  } else {
    alert("method not Found");
    console.log("method not Found");
  }
});

// function addLanguage() {
//   var myanmarText = myanmar.value;
//   var myeikText = myeik.value;

//   // Check if myanmarText is not empty before proceeding
//   if (myanmarText !== "") {
//     // Use setDoc instead of addDoc and provide your own document ID
//     setDoc(doc(db, "data", myanmarText), {
//       value: myeikText,
//     })
//       .then(() => {
//         myanmar.value = "";
//         myeik.value = "";
//         console.log(
//           "Document successfully written with custom ID: ",
//           myanmarText
//         );
//       })
//       .catch((error) => {
//         console.error("Error writing document: ", error);
//       });
//   } else {
//     console.error("myanmarText is empty. Please provide a non-empty value.");
//   }
// }
