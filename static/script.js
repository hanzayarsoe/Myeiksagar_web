import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getFirestore,
  doc,
  getDoc,
  getDocs,
  collection,
  query,
  where,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

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

var text1 = document.getElementById("textarea1");
var text2 = document.getElementById("textarea2");
var translate = document.getElementById("translate");
var dropdown = document.getElementById("dropdown");

var translateBtn = document.getElementById("translateBtn");
var clearBtn = document.getElementById("clearBtn");
var segmentBtn = document.getElementById("segmentBtn");
var swapBtn = document.getElementById("swapBtn");

setTimeout(function () {
  var preloader = document.getElementById("preloader");
  var content = document.getElementById("content");

  // Hide the preloader
  preloader.style.display = "none";
  // Show the website content
  content.style.display = "block";
}, 2000);

let rotationDegree = 0;
function swap() {
  rotationDegree += 180;
  document.getElementById(
    "swapBtn"
  ).style.transform = `rotate(${rotationDegree}deg)`;
  document.getElementById("textarea1").value = "";
  document.getElementById("textarea2").value = "";
  document.getElementById("translate").value = "";

  var spantext1 = document.getElementById("text1").innerText;
  var spantext2 = document.getElementById("text2").innerText;

  document.getElementById("text1").innerText = spantext2;
  document.getElementById("text2").innerText = spantext1;
}
function clearFields() {
  text1.value = "";
  text2.value = "";
  translate.value = "";
  console.log("Cleared Successfully");
}

async function translateMyanmartoMyeik() {
  var myanmarText = text1.value;
  var loadingIndicator = document.getElementById("loadingIndicator");

  // Check if myanmarText is not empty before proceeding
  if (myanmarText.trim() !== "") {
    loadingIndicator.style.display = "block";
    // Use getDoc to retrieve a document by its ID
    myanmarText = myanmarText.replace(/\s/g, "");
    const docRef = doc(db, "data", myanmarText);
    const docSnapshot = await getDoc(docRef);

    if (docSnapshot.exists()) {
      // Display the value in myeikText
      text2.value = docSnapshot.data().value;
      console.log("Document found with ID: ", myanmarText);
    } else {
      console.log("Document not found with ID: ", myanmarText);
      alert(myanmarText + "   ဆိုသည့် စကားလုံးကို ရှာမတွေ့ပါ");
      text1.value = "";
    }
  } else {
    console.error("myanmarText is empty. Please provide a non-empty value.");
    alert(" ကျေးဇူးပြု၍ ပြောင်းလိုသော စားလုံးကိုရေးပေးပါ");
  }
  loadingIndicator.style.display = "none";
}

async function translateMyeiktoMyanmar() {
  var myeikText = text1.value;
  var loadingIndicator = document.getElementById("loadingIndicator");

  if (myeikText.trim() !== "") {
    loadingIndicator.style.display = "block";
    myeikText = myeikText.replace(/\s/g, "");

    const collectionRef = collection(db, "data");
    const q = query(collectionRef, where("value", "==", myeikText));

    try {
      const querySnapshot = await getDocs(q);

      if (!querySnapshot.empty) {
        // Assuming there's only one matching document
        const doc = querySnapshot.docs[0];
        text2.value = doc.id;
        console.log("Document found with ID: ", doc.id);
      } else {
        console.log("No matching documents found for value: ", myeikText);
        alert(myeikText + "   ဆိုသည့် စကားလုံးကို ရှာမတွေ့ပါ");
        text1.value = "";
      }
    } catch (error) {
      console.error("Error getting documents: ", error);
    }
  } else {
    console.error("myeikText is empty. Please provide a non-empty value.");
    alert(" ကျေးဇူးပြု၍ ပြောင်းလိုသော စားလုံးကိုရေးပေးပါ");
  }

  loadingIndicator.style.display = "none";
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

function segmentSyllabus(text) {
  var outArray = text.replace(BREAK_PATTERN, "𝕊$1").split("𝕊");
  if (outArray.length > 0) {
    outArray.shift();
  }
  return outArray;
}

function segmentChar(text) {
  var outArray = text.split("");
  return outArray;
}

function segmentWord(text) {
  try {
    fetch("/translate", {
      method: "POST",
      body: JSON.stringify({ text: text }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Translated text :", data.translated_text);
        document.getElementById("translate").value = data.translated_text;
      })
      .catch((error) => console.error("Error:", error));
  } catch (e) {
    console.log("error: ", e);
  }
}

clearBtn.addEventListener("click", clearFields);
translateBtn.addEventListener("click", () => {
  var source = document.getElementById("text1").innerText;
  if (source == "စံစကား") {
    translateMyanmartoMyeik();
  } else {
    translateMyeiktoMyanmar();
  }
});
swapBtn.addEventListener("click", swap);
segmentBtn.addEventListener("click", () => {
  var selectedMode = dropdown.value;
  if (selectedMode === "syllable") {
    var resultvalue = segmentSyllabus(text1.value);
    translate.value = resultvalue.join(" | ");
  } else if (selectedMode === "character") {
    var resultvalue = segmentChar(text1.value);
    translate.value = resultvalue.join(" | ");
  } else {
    var myanOrMyeik = document.getElementById("text1").innerText;
    if (myanOrMyeik == "ဘိတ်စကား") {
      alert("ဘိတ်စကားအတွက် word ဖြတ်ပေးသော လုပ်ဆောင်ချက်ကို မထည့်သွင်းရသေးပါ");
      text1.value = "";
    } else {
      segmentWord(text1.value);
    }
  }
});
