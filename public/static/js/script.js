import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getFirestore,
  doc,
  getDoc,
  getDocs,
  collection,
  query,
  where,
  limit,
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

const MAX_LOOKUP_CHARS = 200;

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

const text1 = document.getElementById("textarea1");
const text2 = document.getElementById("textarea2");
const translate = document.getElementById("translate");
const dropdown = document.getElementById("dropdown");
const translateBtn = document.getElementById("translateBtn");
const clearBtn = document.getElementById("clearBtn");
const segmentBtn = document.getElementById("segmentBtn");
const swapBtn = document.getElementById("swapBtn");
const loadingIndicator = document.getElementById("loadingIndicator");

setTimeout(function () {
  const preloader = document.getElementById("preloader");
  const content = document.getElementById("content");
  if (preloader) preloader.style.display = "none";
  if (content) content.style.display = "block";
}, 2000);

function notify(message) {
  window.alert(message);
}

function setLoading(isLoading) {
  if (loadingIndicator) {
    loadingIndicator.style.display = isLoading ? "block" : "none";
  }
}

function normalizeLookupText(raw) {
  return (raw || "").replace(/\s+/g, "").trim();
}

function validateLookupText(raw) {
  const text = normalizeLookupText(raw);
  if (!text) {
    notify("ကျေးဇူးပြု၍ ပြောင်းလိုသော စကားလုံးကို ရေးပေးပါ။");
    return null;
  }
  if (text.length > MAX_LOOKUP_CHARS) {
    notify(`စကားလုံးသည် စာလုံး ${MAX_LOOKUP_CHARS} လုံးထက် မကျော်ရပါ။`);
    return null;
  }
  return text;
}

let rotationDegree = 0;
function swap() {
  rotationDegree += 180;
  if (swapBtn) {
    swapBtn.style.transform = `rotate(${rotationDegree}deg)`;
  }

  const temp = text1.value;
  text1.value = text2.value;
  text2.value = temp;

  const label1 = document.getElementById("text1");
  const label2 = document.getElementById("text2");
  if (label1 && label2) {
    const spantext1 = label1.innerText;
    label1.innerText = label2.innerText;
    label2.innerText = spantext1;
  }
}

function clearFields() {
  text1.value = "";
  text2.value = "";
  translate.value = "";
}

async function translateMyanmartoMyeik() {
  const myanmarText = validateLookupText(text1.value);
  if (!myanmarText) return;

  setLoading(true);
  try {
    const docRef = doc(db, "data", myanmarText);
    const docSnapshot = await getDoc(docRef);

    if (!docSnapshot.exists()) {
      text2.value = "";
      notify(`“${myanmarText}” ဆိုသည့် စကားလုံးကို ရှာမတွေ့ပါ။`);
      return;
    }

    const value = docSnapshot.data()?.value;
    if (typeof value !== "string" || !value.trim()) {
      text2.value = "";
      notify("ရရှိသော အချက်အလက် ပုံစံ မမှန်ကန်ပါ။");
      return;
    }
    text2.value = value;
  } catch (error) {
    console.error("Myanmar→Myeik lookup failed:", error);
    text2.value = "";
    notify("ဘာသာပြန်ရာတွင် အမှားဖြစ်နေပါသည်။ ခဏနေမှ ထပ်မံကြိုးစားပါ။");
  } finally {
    setLoading(false);
  }
}

async function translateMyeiktoMyanmar() {
  const myeikText = validateLookupText(text1.value);
  if (!myeikText) return;

  setLoading(true);
  try {
    const collectionRef = collection(db, "data");
    const q = query(collectionRef, where("value", "==", myeikText), limit(1));
    const querySnapshot = await getDocs(q);

    if (querySnapshot.empty) {
      text2.value = "";
      notify(`“${myeikText}” ဆိုသည့် စကားလုံးကို ရှာမတွေ့ပါ။`);
      return;
    }

    text2.value = querySnapshot.docs[0].id;
  } catch (error) {
    console.error("Myeik→Myanmar lookup failed:", error);
    text2.value = "";
    notify("ဘာသာပြန်ရာတွင် အမှားဖြစ်နေပါသည်။ ခဏနေမှ ထပ်မံကြိုးစားပါ။");
  } finally {
    setLoading(false);
  }
}

const myConsonant = "\u1000-\u1021";
const enChar = "a-zA-Z0-9";
const otherChar =
  "\u1023\u1024\u1025\u1026\u1027\u1029\u102a\u103f\u104c\u104d\u104f\u1040-\u1049\u104a\u104b!-/:-@\\[-`\\{-~\\s";
const ssSymbol = "\u1039";
const aThat = "\u103a";

const BREAK_PATTERN = new RegExp(
  `((?!${ssSymbol})[${myConsonant}](?![${aThat}${ssSymbol}])|[${enChar}${otherChar}])`,
  "mg"
);

function segmentSyllabus(text) {
  text = text.replace(/\s/g, "");
  const outArray = text.replace(BREAK_PATTERN, "𝕊$1").split("𝕊");
  if (outArray.length > 0) {
    outArray.shift();
  }
  return outArray;
}

function segmentChar(text) {
  return text.replace(/\s/g, "").split("");
}

async function segmentWord(text) {
  text = text.replace(/\s/g, "");
  setLoading(true);
  try {
    const response = await fetch("/translate", {
      method: "POST",
      body: JSON.stringify({ text }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      notify(data.error || "စာလုံးဖြတ်ရာတွင် အမှားဖြစ်နေပါသည်။");
      return;
    }
    if (typeof data.translated_text !== "string") {
      notify("စာလုံးဖြတ်ရလဒ် ပုံစံ မမှန်ကန်ပါ။");
      return;
    }
    translate.value = data.translated_text;
  } catch (error) {
    console.error("Word segmentation failed:", error);
    notify("စာလုံးဖြတ်ရာတွင် အမှားဖြစ်နေပါသည်။ ခဏနေမှ ထပ်မံကြိုးစားပါ။");
  } finally {
    setLoading(false);
  }
}

clearBtn.addEventListener("click", clearFields);
translateBtn.addEventListener("click", () => {
  const source = document.getElementById("text1")?.innerText;
  if (source === "စံစကား") {
    translateMyanmartoMyeik();
  } else {
    translateMyeiktoMyanmar();
  }
});
swapBtn.addEventListener("click", swap);
segmentBtn.addEventListener("click", () => {
  if (!translate.value.trim()) {
    notify("ကျေးဇူးပြု၍ ဖြတ်လိုသောစာကို ရေးပေးပါ။");
    return;
  }

  const selectedMode = dropdown.value;
  if (selectedMode === "syllable") {
    translate.value = segmentSyllabus(translate.value).join("   ");
  } else if (selectedMode === "character") {
    translate.value = segmentChar(translate.value).join("   ");
  } else {
    segmentWord(translate.value);
  }
});
