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

const MAX_PHRASE_CHARS = 500;
const MAX_TOKEN_CHARS = 200;
const COLLECT_APP_URL = "https://myeiksagar-collect.vercel.app/";
const MISSING_MARK = (token) => `[${token}]`;

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
const translationStatus = document.getElementById("translationStatus");

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

function normalizePhrase(raw) {
  return (raw || "").replace(/\s+/g, "").trim();
}

function validatePhrase(raw) {
  const text = normalizePhrase(raw);
  if (!text) {
    notify("ကျေးဇူးပြု၍ ပြောင်းလိုသော စကားလုံး/စာကြောင်းကို ရေးပေးပါ။");
    return null;
  }
  if (text.length > MAX_PHRASE_CHARS) {
    notify(`စာသားသည် စာလုံး ${MAX_PHRASE_CHARS} လုံးထက် မကျော်ရပါ။`);
    return null;
  }
  return text;
}

function collectUrlFor(word) {
  const url = new URL(COLLECT_APP_URL);
  url.searchParams.set("word", word);
  return url.toString();
}

function clearTranslationStatus() {
  if (!translationStatus) return;
  translationStatus.classList.add("hidden");
  translationStatus.innerHTML = "";
}

function renderTranslationStatus({ found, missing, mode }) {
  if (!translationStatus) return;

  if (!missing.length && found > 0) {
    translationStatus.classList.remove("hidden");
    translationStatus.innerHTML = `
      <p class="ms-status__ok">
        အဘိဓာန်တွင် စကားလုံး ${found} လုံး အပြည့်အဝ တွေ့ရှိပါသည်။
      </p>
    `;
    return;
  }

  if (!found && !missing.length) {
    clearTranslationStatus();
    return;
  }

  const directionHint =
    mode === "myeik-to-myanmar"
      ? "ဘိတ် → စံ"
      : "စံ → ဘိတ်";

  const missingLinks = missing
    .map(
      (word) => `
      <a
        href="${collectUrlFor(word)}"
        target="_blank"
        rel="noopener noreferrer"
        class="ms-chip"
        title="Insert Data တွင် ထည့်ရန်"
      >${word}</a>`
    )
    .join(" ");

  translationStatus.classList.remove("hidden");
  translationStatus.innerHTML = `
    <p class="ms-status__line">
      <strong>${directionHint}</strong> —
      တွေ့ရှိ ${found} လုံး၊ မရှိသေး ${missing.length} လုံး။
      မရှိသော စကားလုံးများကို <code>[...]</code> ဖြင့် ပြထားပါသည်။
    </p>
    <p class="ms-status__line">အဘိဓာန်သို့ ထည့်ရန် (Insert Data):</p>
    <div class="ms-chip-row">${missingLinks}</div>
  `;
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
  clearTranslationStatus();
}

function clearFields() {
  text1.value = "";
  text2.value = "";
  translate.value = "";
  clearTranslationStatus();
}

async function lookupMyanmarToMyeik(token) {
  if (!token || token.length > MAX_TOKEN_CHARS) return null;
  const snapshot = await getDoc(doc(db, "data", token));
  if (!snapshot.exists()) return null;
  const value = snapshot.data()?.value;
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

async function lookupMyeikToMyanmar(token) {
  if (!token || token.length > MAX_TOKEN_CHARS) return null;
  const q = query(
    collection(db, "data"),
    where("value", "==", token),
    limit(1)
  );
  const snapshot = await getDocs(q);
  if (snapshot.empty) return null;
  return snapshot.docs[0].id;
}

async function fetchWordTokens(text) {
  const response = await fetch("/translate", {
    method: "POST",
    body: JSON.stringify({ text }),
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "segmentation failed");
  }
  if (typeof data.translated_text !== "string") {
    throw new Error("invalid segmentation response");
  }
  return data.translated_text.split(/\s+/).filter(Boolean);
}

function tokensFromWhitespaceOrSyllables(text) {
  const spaced = text.trim().split(/\s+/).filter(Boolean);
  if (spaced.length > 1) return spaced;
  const syllables = segmentSyllabus(text);
  return syllables.length ? syllables : [normalizePhrase(text)];
}

async function translatePhrase({
  sourceText,
  lookupExact,
  lookupToken,
  tokenize,
  mode,
}) {
  const phrase = validatePhrase(sourceText);
  if (!phrase) return;

  setLoading(true);
  clearTranslationStatus();
  try {
    const exact = await lookupExact(phrase);
    if (exact) {
      text2.value = exact;
      renderTranslationStatus({ found: 1, missing: [], mode });
      return;
    }

    const tokens = await tokenize(phrase);
    if (!tokens.length) {
      text2.value = "";
      notify("စာသားကို စကားလုံးခွဲ၍ မရပါ။");
      return;
    }

    const parts = [];
    const missing = [];
    let found = 0;

    for (const token of tokens) {
      const hit = await lookupToken(token);
      if (hit) {
        parts.push(hit);
        found += 1;
      } else {
        parts.push(MISSING_MARK(token));
        if (!missing.includes(token)) missing.push(token);
      }
    }

    text2.value = parts.join(" ");
    renderTranslationStatus({ found, missing, mode });

    if (!found) {
      notify("အဘိဓာန်တွင် ကိုက်ညီသော စကားလုံး မတွေ့ပါ။ အောက်မှ Insert Data လင့်ခ်ဖြင့် ထည့်နိုင်ပါသည်။");
    }
  } catch (error) {
    console.error("Phrase translation failed:", error);
    text2.value = "";
    clearTranslationStatus();
    notify("ဘာသာပြန်ရာတွင် အမှားဖြစ်နေပါသည်။ ခဏနေမှ ထပ်မံကြိုးစားပါ။");
  } finally {
    setLoading(false);
  }
}

async function translateMyanmartoMyeik() {
  await translatePhrase({
    sourceText: text1.value,
    mode: "myanmar-to-myeik",
    lookupExact: lookupMyanmarToMyeik,
    lookupToken: lookupMyanmarToMyeik,
    tokenize: fetchWordTokens,
  });
}

async function translateMyeiktoMyanmar() {
  await translatePhrase({
    sourceText: text1.value,
    mode: "myeik-to-myanmar",
    lookupExact: lookupMyeikToMyanmar,
    lookupToken: lookupMyeikToMyanmar,
    tokenize: async (phrase) => tokensFromWhitespaceOrSyllables(phrase),
  });
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
