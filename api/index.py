import os
import random
import pycrfsuite
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)

# create segment function


# open trained model
tagger = pycrfsuite.Tagger()
tagger.open('./api/mm-word-segmentation-300.crfsuite')

# here sentence is prepared_sentence and i is length of prepared_sentence


def create_char_features(sentence, i):
    # set initial feature set char as first char in prepared_sentence
    features = [
        'bias',
        'char=' + sentence[i][0]
    ]
    # if i >=1 then go to previous character else append 'BOS' in features list
    if i >= 1:
        features.extend([
            'char-1=' + sentence[i-1][0],
            'char-1:0=' + sentence[i-1][0] + sentence[i][0],
        ])
    else:
        features.append("BOS")

    if i >= 2:
        features.extend([
            'char-2=' + sentence[i-2][0],
            'char-2:0=' + sentence[i-2][0] + sentence[i-1][0] + sentence[i][0],
            'char-2:-1=' + sentence[i-2][0] + sentence[i-1][0],
        ])

    if i >= 3:
        features.extend([
            'char-3:0=' + sentence[i-3][0] + sentence[i -
                                                      2][0] + sentence[i-1][0] + sentence[i][0],
            'char-3:-1=' + sentence[i-3][0] +
            sentence[i-2][0] + sentence[i-1][0],
        ])
    # if i+1 < len(sentence) then go to next character and set it to next character and set char to next two characters else append 'EOS' to features list
    if i + 1 < len(sentence):
        features.extend([
            'char+1=' + sentence[i+1][0],
            'char:+1=' + sentence[i][0] + sentence[i+1][0],
        ])
    else:
        features.append("EOS")
    # if first if condition satisfy then go to second and third if condition and do the same work for next characters
    if i + 2 < len(sentence):
        features.extend([
            'char+2=' + sentence[i+2][0],
            'char:+2=' + sentence[i][0] + sentence[i+1][0] + sentence[i+2][0],
            'char+1:+2=' + sentence[i+1][0] + sentence[i+2][0],
        ])

    if i + 3 < len(sentence):
        features.extend([
            'char:+3=' + sentence[i][0] + sentence[i +
                                                   1][0] + sentence[i+2][0] + sentence[i+3][0],
            'char+1:+3=' + sentence[i+1][0] +
            sentence[i+2][0] + sentence[i+3][0],
        ])
    return features


def create_word_features(prepared_sentence):
    return [create_char_features(prepared_sentence, i) for i in range(len(prepared_sentence))]

# segment word by trained model


def segment_word(sentence):
    # remove white spaces from sentence
    sent = sentence.replace(" ", "")
    # tag sentence by trained model or create sentence features
    prediction = tagger.tag(create_word_features(sent))
    # assign 'complete' to empty string
    complete = ""
    # apply for loop on taged sentence
    for i, p in enumerate(prediction):
        # if label of character in sentence is 1 then brack that word from that place and add into complete
        if p == "1":
            complete += "   " + sent[i]
        # if label of character in sentence is 0 then add that word as it is into complete
        else:
            complete += sent[i]
    # print(type(sent))
    return complete

# Quiz app logic


questions = {
    'easy': [
        {'question': 'မြိတ်ဒေသ၏ ထင်ရှားသောအစားအစာသည် မည်သည့်အစားအစာဖြစ်ပါသလဲ။',
            'options': ['ဇွန်းကိုက်', 'ကိုက်ကြေးကိုက်', 'ခရင်းကိုက်', 'ဇံကိုက်'], 'answer': 'ကိုက်ကြေးကိုက်'},
        {'question': 'မြိတ်ကျွန်းစုမှ ထွက်ရှိသော တန်ဖိုးကြီးရတနာမှာ မည်သည့်ပစ္စည်းဖြစ်ပါသလဲ။', 'options': [
            'ရွှေ', 'ငွေ', 'ပုလဲ', 'ပတ္တမြား'], 'answer': 'ပုလဲ'},
        {'question': 'မြိတ်မြို့ကို ရှေးယခင်အခါက မည်သို့ခေါ်ဆိုခဲ့ပါသလဲ။',
            'options': ['ဘိတ်', 'မာရိတ်', 'မြိတ်', 'မာရီ'], 'answer': 'မာရိတ်'},
        {'question': 'ပထော်ပထက်သည် မြိတ်မြို့၏ မည်သည့်အရပ်တွင်ရှိပါသနည်း။',
            'options': ['အရှေ့', 'အနောက်', 'တောင်', 'မြောက်'], 'answer': 'အနောက်'},
        {'question': 'မြိတ်ဒေသတွင် ပြတင်းပေါက် ကိုမည်သို့ခေါ်ဆိုပါသနည်း။',
            'options': ['ပန်းတင်းပေါက်', 'လက်တံပေါက်', 'တလာပါပေါက်', 'ပြတင်းပေါက်'], 'answer': 'လက်တံပေါက်'},
        {'question': 'မြိတ်ဒေသတွင် မိမိ၏ချစ်သူကို မည်သို့ ခေါ်ပါသနည်း။', 'options': [
            'ရည်းစား', 'ရဲစား', 'ချစ်သူ', 'ကြင်သူသက်ထား'], 'answer': 'ရဲစား'},
        {'question': 'မြိတ်ဒေသတွင် ရေခဲမုန့်ကို မည်သို့ခေါ်ဆိုကြပါသလဲ။',
            'options': ['ရေခဲမုန့်', 'ရေခဲလုံး', 'အုန်းမွှေး', 'ရေခဲခြစ်'], 'answer': 'အုန်းမွှေး'},
        {'question': 'မြိတ်ဒေသတွင် မနက်ဖြန် ကိုမည်သို့ခေါ်ကြပါသနည်း။', 'options': [
            'နက်ဖြန်', 'မိုးလင်းတိုင်', 'မိုးစင်စင်', 'မိုးတိုင်'], 'answer': 'မိုးလင်းတိုင်'},
        {'question': 'မြိတ်ဒေသတွင် သင်္ဘောသီးကို မည်သို့ခေါ်ဆိုကြပါသနည်း။', 'options': [
            'တောင်စွယ်သီး', 'စိန်ခွားသီး', 'မိုးမျှော်သီး', 'ရှိန်းခိုသီး'], 'answer': 'ရှိန်းခိုသီး'},
        {'question': 'မြိတ်ဒေသတွင် ဖရဲသီးကို မည်သို့ခေါ်ဆိုကြပါသနည်း။', 'options': [
            'တောင်စွယ်သီး', 'ရှိန်းခိုသီး', 'မိုးမျှော်သီး', 'စိန်ခွားသီး'], 'answer': 'စိန်ခွားသီး'},
        {'question': 'မြိတ်ဒေသတွင် အဓိကထားလုပ်ကိုင်သောလုပ်ငန်းများအနက် မည်သည့်လုပ်ငန်းကို အများဆုံးလုပ်ကိုင်ကြပါသနည်း။', 'options': [
            'ရေလုပ်ငန်း', 'ဥယျာဉ်ခြံလုပ်ငန်း', 'ရာဘာလုပ်ငန်း', 'ကုန်ရောင်းကုန်ဝယ်လုပ်ငန်း'], 'answer': 'ရေလုပ်ငန်း'},
        {'question': 'မြိတ်မြို့တွင် နေထိုင်ခဲ့သော နာမည်ကြီး ရုပ်ရှင်သရုပ်ဆောင်မာ မည်သူဖြစ်ပါသနည်း။', 'options': [
            'နေတိုင်း', 'ဟိန်းဝေယံ', 'လွင်မိုး', 'မြင့်မြတ်'], 'answer': 'လွင်မိုး'},
        {'question': 'မြိတ်မြို့ရှိလျောင်းတော်မူဘုရားသည် မည်သည့်တောင်တွင် တည်ရှိပါသနည်း။', 'options': [
            'ပထော်', 'ပထက်', 'ကျွန်းစု', 'ရွှေသာလျောင်း'], 'answer': 'ပထက်'},
        {'question': 'မြိတ်မြို့တွင် သမိုင်းဝင်ဘုရားစုံ ဘယ်နှစ်စုံရှိပါသနည်း။', 'options': [
            '၃', '၄', '၅', '၆'], 'answer': '၄'},
    ],
    'medium': [
        {'question': 'မြိတ်ခရိုင်တွင် မြို့နယ် ဘယ်နှစ်ခု ပါဝင်ပါသနည်း', 'options': [
            '၁', '၂', '၃', '၄'], 'answer': '၄'},
        {'question': 'မြိတ်မြို့တွင် ရပ်ကွက်ပေါင်းမည်မျှရှိပါသနည်း။', 'options': [
            '၂၀', '၂၇', '၁၉', '၃၅'], 'answer': '၂၇'},
        {'question': 'မြိတ်မြို့၏ သိမ်တော်ကြီးဘုရားအနီးတွင်ရှိသော အုတ်ဂူသည် မည်သူ့၏အုတ်ဂူပါလဲ။', 'options': [
            'ဥိီးမြတ်လေး', 'ဥိီးအောင်ဇေယျ', 'လင်းပင်ထိပ်တင်ဒွေး', 'ပရမရာစာ'], 'answer': 'လင်းပင်ထိပ်တင်ဒွေး'},
        {'question': 'သိမ်တော်ကြီးတည်ရှိရာ ကုန်းတော်သည် မည်သည့်ကုန်းတော်ဖြစ်ပါသနည်း။',
            'options': ['ကိုးနဝင်းတောင်', 'ခယ်တောင်', 'သိမ်ကြီးတောင်', 'သိင်္ဂုတ္တရတောင်'], 'answer': 'ခယ်တောင်'},
        {'question': 'ပထက်တောင်တွင်ရှိသော လျောင်းတော်မူဘုရား၏ ဘွဲ့အမည်မှာ',
            'options': ['တိလောကဥသျှောင်လျောင်းတော်မူဘုရား', 'လောကသရဖူလျောင်းတော်မူဘုရား', 'ရွှေသာလျောင်းဘုရား', 'အတုလရံသီရွှေသာလျောင်းဘုရား'], 'answer': 'အတုလရံသီရွှေသာလျောင်းဘုရား'},
        {'question': 'မြိတ်မြို့၏ လျောင်းတော်မူဘုရားသည် မြန်မာနိုင်ငံ၏ဘယ်နှစ်ခုမြောက်အကြီးဆုံးဖြစ်ပါသနည်း။ ', 'options': [
            'ပဥ္စမမြောက်', 'သတ္တမမြောက်', 'ဆဌမမြောက်', 'အဌမမြောက်'], 'answer': 'သတ္တမမြောက်'},
        {'question': 'ကြောင်တောင်တောင်နိုင်သည်ကို မြိတ်တွင်မည်သို့ခေါ်ဆိုကြပါသနည်း။',
            'options': ['အုတ်အက်မစေ့', 'အောလီအောလက်', 'ဗုန်းစဲဗုန်းစဲ', 'ရှောလောကာ'], 'answer': 'အောလီအောလက်'},
        {'question': 'မြိတ်မြို့၏ရာသီဥတု အမျိုးအစားသည် မည်သည့်ရာသီဥတုအမျိုးအစားဖြစ်ပါသလဲ။',
            'options': ['မုတ်သုံရာသီဥတု', 'ခြောက်သွေ့သောဥတု', 'အပူပိုင်းမုတ်သုံရာသီဥတု', 'အေးသောဥတု'], 'answer': 'အပူပိုင်းမုတ်သုံရာသီဥတု'},
        {'question': 'မြိတ်မြို့တွင် လူသိများသော အာပုံဆိုင်မာ မည်သည့်နေရာတွင်ရှိပါသနည်း။', 'options': [
            'စမ်းချောင်း', 'တပ်ပြင်', 'ထားဝယ်စု', 'စန္ဒဝတ်'], 'answer': 'စန္ဒဝတ်'},
        {'question': 'မြိတ််မြို့သည် မည်သည့်တိုင်းဒေသကြီးအတွင်းတွင်တည်ရှိပါသနည်း။',
            'options': ['ရန်ကုန်တိုင်းဒေသကြီး', 'တနင်္သာရီတိုင်းဒေသကြီး', 'ဧရာဝတီတိုင်းဒေသကြီး', 'ပဲခူးတိုင်းဒေသကြီး'],
            'answer': 'တနင်္သာရီတိုင်းဒေသကြီး'},
        {'question': 'မြိတ်မြို့ဝန် ပဲတောင်းစားမင်းတည်ခဲ့သော ပဲတောင်စားစေတီသည် မည်သည့်နေရာတွင်ရှိပါသနည်း။',
            'options': ['ဘုရားကြီးလမ်း', 'သိမ်တော်ကြီးဘုရား', 'ဗူးဘုရား', 'ဝတ်တိုက်ကျောင်းတိုက်'],
            'answer': 'သိမ်တော်ကြီးဘုရား'},
        {'question': 'မြိတ်မြို့ရှိ ကန်ကြီးရေကန်ဘောင်ရဲ့ မူလအမည်မှာ မည်သည်ဖြစ်ပါသနည်း။',
            'options': ['ရေကန်တော်', 'ကန်တော်မင်္ဂလာ', 'ပဲတောင့်မင်းကန်', 'ဥဒေါင်းမင်းကန်'],
            'answer': 'ဥဒေါင်းမင်းကန်'},
        {'question': 'မြန်မာလူမျိုး မြိတ်မြိို့ဝန်နောက်ဆုံးမင်းမှာ မည်သူဖြစ်ပါသနည်း။',
            'options': ['မြို့ဝန်မင်းရန်ကူး', 'မြို့ဝန်ဥိီးနေမင်း', 'မြို့ဝန်ဥိီးမြတ်လေး', 'မြို့ဝန်ပဲတောင်းစား'],
            'answer': 'မြို့ဝန်ဥိီးမြတ်လေး'},
        {'question': 'ကျောက်ဖျာမြစ်ပေါ်တံတား ဘယ်နှစ်ရှိပါသလဲ။',
            'options': ['၁', '၂', '၃', '၄'],
            'answer': '၂'},
        {'question': 'စုံလေးစုံတွင် တစ်ပြိုင်တည်း တည်သော စုံနှစ်စုံမှာ',
            'options': ['ဖနုံးစုံ‌စေတီနှင့် မဏိစုံစေတီ', 'ဗလပ်စုံနှင့် ဘုတ်စုံစေတီ', 'ဗလပ်စုံနှင့် မဏိစုံစေတီ', 'ဖနုံးစုံစေတီနှင့် မဏိစုံစေတီ'],
            'answer': 'ဗလပ်စုံနှင့် မဏိစုံစေတီ'},
        {'question': 'မြိတ်မြို့၏ ကွန်ပျူတာ တက္ကသိုလ်အနီးတွင် တည်ရှိသော စုံရဲ့အမည်မှာ',
            'options': ['ဘုတ်စုံ', 'မဏိစုံ', 'ဗလပ်စုံ', 'ဖနုံးစုံ'],
            'answer': 'ဖနုံးစုံ'},
        {'question': 'မြိတ်မြို့တွင်ရှိသော ကျောက်စရစ်ခဲအလွန်ပေါများသော ကျွန်းမာ မည်သည့်ကျွန်းဖြစ်သနည်း။',
            'options': ['လေးကျွန်း', 'ကျွန်းဘုရင်', 'ပါပန့်ကျွန်း', 'ဒုံးကျွန်း'],
            'answer': 'ပါပန့်ကျွန်း'},

    ],
    'hard': [
        {'question': 'မြိတ်မြို့ကို မည်သည့်မြို့ဝန်မင်းလက်ထက်တွင် မြိတ်မြို့ဟု တရားဝင်ခေါ်ဆိုခဲ့ပါသနည်း။', 'options': [
            'ဆင်ဖြူရှင်', 'အယုဒ္ဓယ', 'အလောင်းဘုရား', 'ခေမရစာ'], 'answer': 'ခေမရစာ'},
        {'question': 'မြိတ်ဒေသကို မည်သူက စတင်တည်ထောင်ခဲ့ပါသနည်း။',
            'options': ['အလောင်းမင်းတရားကြီးဥိီးအောင်ဇေယျ', 'ဆင်ဖြူရှင်မင်း', 'ဗြိရာမသွန်တဿ', 'စောလူးမင်း'], 'answer': 'ဗြိရာမသွန်တဿ'},
        {'question': 'မြိတ်မြို့ကို မည်သည့်ခုနှစ်ရောက်မှ အပြီးသတ်တည်ဆောက်ပြီးစီးခဲ့ပါသနည်း။', 'options': [
            '၁၄၅၀', '၁၉၉၀', '၁၈၄၀', '၁၇၇၀'], 'answer': '၁၇၇၀'},
        {'question': 'မည်သည့် ခုနှစ်တွင် မြိတ်မြို့သည် ပထမ အင်္ဂလိပ်မြန်မာစစ်ပွဲဲ၌ ကိုလိုနီလက်အောက်သို့ကျရောက်ခဲ့ပါသနည်း။',
            'options': ['၁၇၅၀', '၁၈၂၄', '၁၉၀၀', '၁၈၁၄'], 'answer': '၁၈၂၄'},
        {'question': 'မြိတ်မြို့ရှိ ပေါ်တော်မူ ဘုရားသည် မည်သည့်တောင်ကုန်းပေါ်တွင် တည်ထားကိုးကွယ်ထားပါသနည်း။', 'options': [
            'သိင်္ဂုတ္တရကုန်းတော်', 'အောင်သိဒ္ဓိကုန်းတော်', 'ခယ်မာကုန်းတော်', 'သီရိကုမ္မာကုန်းတော်'], 'answer': 'အောင်သိဒ္ဓိကုန်းတော်'},
        {'question': 'အေဒီ ၁၇၅၉ တွင် မည်သည့်မင်းသည် မြိတ်မြို့ကို မြန်မာနိုင်ငံအတွင်းသို့ ပြန်လည်ရောက်ရှိအောင် လုပ်ဆောင်ခဲ့ပါသနည်း။',
            'options': ['အလောင်းမင်းတရားကြီးဥိီးအောင်ဇေယျ', 'တပင်ရွှေထီး', 'ဘုရင့်နောင်', 'ဆင်ဖြူရှင်'], 'answer': 'အလောင်းမင်းတရားကြီးဥိီးအောင်ဇေယျ'},
        {'question': 'မြိတ်မြို့သည် ပင်လယ်ရေမျက်နှာပြင်အမြင့်ပေ မည်မျှတွင်တည်ရှိပါသနည်း။', 'options': [
            '၁၀', '၅၄', '၃၉', '၈၄'], 'answer': '၈၄'},
        {'question': 'မြိတ်မြို့ရှိ ပြည်လုံးချမ်းသာကမ္ဘာလုံးစေတီတော်မြတ်ကြီးကို မည်သည့်တောင်ကုန်းပေါ်တွင် တည်ထားကိုးကွယ်ထားပါသနည်း။',
            'options': ['ငွေနန်းတောင်ကုန်း', 'ရွှေနန်းတောင်ကုန်း', 'ပုလဲတောင်ကုန်း', 'သိမ်ဖြူတောင်ကုန်း'], 'answer': 'ရွှေနန်းတောင်ကုန်း'},
        {'question': 'မြိတ်မြို့ရှိ ကျွဲကူးတံတား၏ အရှည်မာ မည်မျှဖြစ်ပါသနည်း', 'options': [
            '၄၉၃၉ ‌ပေ', '၃၇၆၀ ‌ပေ', '၃၆၁၂ ‌ပေ', '၅၉၈၃ ‌ပေ'], 'answer': '၃၆၁၂ ‌ပေ'},
        {'question': 'မြိတ်မြို့ရှိလေးကျွန်းဆီမီးသိမ်တော်ကြီးကို မြန်မာသက္ကရာဇ်မည်သည့်ခုနှစ်တွင် စတင်တည်ထောင်ခဲ့ပါသနည်း။',
            'options': ['၁၀၉၄', '၁၀၉၅', '၁၀၉၃', '၁၀၉၂'], 'answer': '၁၀၉၃'},
        {'question': 'လေးကျွန်းဆီမီးသိမ်တော်ကြီးကို ရှေးယခင်က မည်သို့ ခေါ်ဆိုခဲ့ကြပါသနည်း။', 'options': [
            'သိမ်တော်ကြီး', 'လေးကျွန်းသိမ်တော်ကြီး', 'ခယ်လှစေတီ', 'ခယ်တောင်စေတီ'], 'answer': 'မိုးလင်းတိုင်'},
    ]
}


@app.route('/quiz_start_page')
def quiz_start_page():
    return render_template('quiz_start_page.html')


@app.route('/quiz_start')
def quiz_start():
    session.clear()
    session['level'] = 'easy'
    session['score'] = 0
    session['question_number'] = 0
    session['completed_levels'] = 0

    # Get all questions for the current level
    available_questions = questions[session['level']]

    # Always set the number of questions to 10
    num_questions = 10

    # If there are fewer than 10 questions available, repeat some questions
    if len(available_questions) < num_questions:
        session['questions'] = random.choices(
            available_questions, k=num_questions)
    else:
        session['questions'] = random.sample(
            available_questions, num_questions)

    # Store the total number of questions for this round
    session['total_questions'] = num_questions

    return redirect(url_for('quiz'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'level' not in session:
        return redirect(url_for('quiz_start_page'))

    if request.method == 'POST':
        user_answer = request.form['answer'].lower()
        correct_answer = session['questions'][session['question_number']]['answer'].lower(
        )

        if user_answer == correct_answer:
            session['score'] += 1

        session['question_number'] += 1

        if session['question_number'] >= session['total_questions']:
            if session['score'] == session['total_questions']:
                session['completed_levels'] += 1
                if session['level'] == 'hard':
                    return redirect(url_for('congratulations'))
                else:
                    return redirect(url_for('next_level'))
            else:
                return redirect(url_for('result'))

    if session['question_number'] < session['total_questions']:
        question_data = session['questions'][session['question_number']]
        question = question_data['question']
        options = question_data['options']
        return render_template('quiz.html', question=question, options=options, level=session['level'],
                               question_number=session['question_number'] + 1,
                               total_questions=session['total_questions'])
    else:
        return redirect(url_for('result'))


@app.route('/next_level')
def next_level():
    if 'completed_levels' not in session or session['completed_levels'] < 1:
        return redirect(url_for('quiz_start_page'))
    next_level = 'medium' if session['level'] == 'easy' else 'hard'
    return render_template('next_level.html', next_level=next_level)


@app.route('/start_next_level')
def start_next_level():
    if 'completed_levels' not in session or session['completed_levels'] < 1:
        return redirect(url_for('quiz_start_page'))
    if session['level'] == 'easy':
        session['level'] = 'medium'
    elif session['level'] == 'medium':
        session['level'] = 'hard'

    session['score'] = 0
    session['question_number'] = 0
    session['questions'] = random.sample(questions[session['level']], 10)
    return redirect(url_for('quiz'))


@app.route('/congratulations')
def congratulations():
    if 'completed_levels' not in session or session['completed_levels'] < 3:
        return redirect(url_for('quiz_start_page'))
    # Reset completed levels after showing congratulations
    session['completed_levels'] = 0
    return render_template('congratulations.html')


@app.route('/result')
def result():
    if 'level' not in session:
        return redirect(url_for('quiz_start_page'))
    return render_template('result.html', score=session['score'], level=session['level'])


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/translate', methods=['POST'])
def wordTranslation():
    data = request.json
    text_to_translate = data.get('text')
    translated_text = segment_word(text_to_translate)

    return jsonify({'translated_text': translated_text})


if __name__ == '__main__':
    app.run(debug=True)
