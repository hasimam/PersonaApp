# دليل إعداد مجموعات Deep (للخبراء الخارجيين)

آخر تحديث: 2026-02-15

## 1) الهدف

يوضح هذا الدليل طريقة إعداد وتسليم **مجموعة Deep واحدة** بصيغة واضحة وجاهزة للمراجعة والاستيراد من فريق PersonaApp.

## 2) ما الذي يجب تسليمه

يرجى تسليم أحد الخيارين:
- ملف Excel واحد (`.xlsx`) يحتوي على 3 أوراق، أو
- 3 ملفات CSV منفصلة.

الأوراق/الملفات المطلوبة:
- `scenarios`
- `options`
- `weights`

## 3) مواصفات مجموعة Deep

يجب أن تحتوي المجموعة الواحدة على:
- `version_id`: دائما `v2`
- `scenario_set_code`: كود مجموعة جديد وفريد (مثال: `deep_12`)
- عدد المواقف: **48** بالضبط
- عدد الخيارات لكل موقف: **4** بالضبط (`A`, `B`, `C`, `D`)

## 4) أكواد الجينات المسموح بها (Deep v2)

استخدم فقط أكواد الجينات العشرين التالية داخل الأوزان:

| الرمز | الاسم الانجليزي         | الاسم العربي              |
| ----- | ----------------------- | ------------------------- |
| LOVE  | Love & Care             | الحب والرعاية             |
| ACHV  | Achievement             | الإنجاز                   |
| JOY   | Happiness & Contentment | السعادة والرضا            |
| FREE  | Autonomy                | الاستقلالية               |
| SAFE  | Safety & Security       | الأمن                     |
| HLTH  | Health & Wellness       | الصحة والعافية            |
| DIGN  | Dignity & Respect       | الكرامة والاحترام         |
| JUST  | Justice & Fairness      | العدالة والمساواة         |
| FRND  | Friendship              | الصداقة                   |
| LEARN | Learning & Knowledge    | التعلم والمعرفة           |
| SPIR  | Meaning & Purpose       | المعنى والغاية            |
| FINC  | Financial Stability     | الاستقرار المالي          |
| RECO  | Recognition             | التقدير والاعتراف         |
| ADVN  | Adventure & Challenge   | المغامرة والتحدي          |
| ARTS  | Beauty & Art            | الجمال والفن              |
| FUN   | Fun & Enjoyment         | المرح والترفيه            |
| COMM  | Community & Belonging   | الانتماء والمجتمع         |
| AMBT  | Ambition & Growth       | الطموح والتطور            |
| GRAT  | Gratitude               | الامتنان                  |
| BALN  | Work-Life Balance       | التوازن بين العمل والحياة |

## 5) قواعد إعداد مجموعات Deep

### 5.1 قواعد بنيوية (إلزامية)
- استخدم كود مجموعة واحدا بشكل متسق في جميع الصفوف (مثال: `deep_12`).
- يجب أن تحتوي المجموعة على 48 موقفا بالضبط.
- اجعل `order_index` من `1` إلى `48` بدون أي فجوات.
- كل موقف يجب أن يحتوي على 4 خيارات فقط: `A`, `B`, `C`, `D`.
- كل خيار يجب أن يكون له سطر وزن واحد على الأقل في `weights`.
- `scenario_code` يجب أن يكون فريدا داخل المجموعة (مثال: `D12_01` ... `D12_48`).

### 5.2 قواعد لغوية (إلزامية)
- توفير النص بالإنجليزية والعربية لكل موقف وخيار.
- العربية فصحى حديثة، طبيعية، وبدون تشكيل.
- الصياغة قصيرة وواضحة وسلوكية.
- يجب أن تكون الخيارات مختلفة بوضوح في السلوك.

### 5.3 قواعد الأوزان (إلزامية)
- كل سطر وزن يربط خيارا واحدا بجين واحد وقيمة وزن رقمية.
- يوصى بالأوزان الموجبة (النمط الشائع: `2`).
- مسموح بتوزيع وزن الخيار على أكثر من جين (مثال: `ACHV=1` و `BALN=1` لنفس الخيار).
- يفضل توازن مجموع الأوزان بين خيارات نفس الموقف.

### 5.4 قواعد التغطية (موصى بها)
- يفضل أن تظهر الجينات العشرون كلها مرة واحدة على الأقل عبر المجموعة الكاملة.
- وزع السياقات (العائلة، الأصدقاء، العمل/الدراسة، الصحة، المجتمع، القرارات الشخصية).
- تجنب تكرار مواقف متشابهة جدا.

## 6) خطوات العمل المباشرة

1. اختر كود مجموعة جديد (مثال: `deep_12`).
2. اكتب 48 موقفا (إنجليزي + عربي) مع `order_index`.
3. اكتب 4 خيارات (`A/B/C/D`) لكل موقف (إنجليزي + عربي).
4. اربط كل خيار بأوزان باستخدام أكواد الجينات المسموح بها فقط.
5. راجع قائمة التحقق في القسم 8.
6. أرسل الملفات إلى جهة التواصل في PersonaApp.

## 7) القوالب + مثال كامل (موقف واحد)

### 7.1 قالب `scenarios`

الأعمدة:
- `version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar`

مثال:

```csv
version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar
v2,D12_01,deep_12,1,Your team asks you to lead a stressful task this week.,فريقك يطلب منك قيادة مهمة ضاغطة هذا الأسبوع.
```

### 7.2 قالب `options`

الأعمدة:
- `version_id,scenario_code,option_code,option_text_en,option_text_ar`

مثال:

```csv
version_id,scenario_code,option_code,option_text_en,option_text_ar
v2,D12_01,A,Accept and divide the work clearly.,أقبل المهمة وأقسم العمل بوضوح.
v2,D12_01,B,Accept but ask for support and check-ins.,أقبل المهمة وأطلب دعما ومتابعة دورية.
v2,D12_01,C,Delay decision until priorities are reviewed.,أؤجل القرار حتى أراجع الأولويات.
v2,D12_01,D,Decline and protect current commitments.,أعتذر للحفاظ على التزاماتي الحالية.
```

### 7.3 قالب `weights`

الأعمدة:
- `version_id,scenario_code,option_code,gene_code,weight`

مثال وزن أحادي لكل خيار:

```csv
version_id,scenario_code,option_code,gene_code,weight
v2,D12_01,A,ACHV,2
v2,D12_01,B,COMM,2
v2,D12_01,C,BALN,2
v2,D12_01,D,FREE,2
```

مثال صحيح لوزن موزع لنفس الخيار:

```csv
version_id,scenario_code,option_code,gene_code,weight
v2,D12_01,A,ACHV,1
v2,D12_01,A,BALN,1
v2,D12_01,B,COMM,2
v2,D12_01,C,BALN,2
v2,D12_01,D,FREE,2
```

## 8) قائمة التحقق قبل التسليم

- 48 موقفا مكتملة.
- `order_index` من 1 إلى 48 بدون فجوات.
- كل موقف له 4 خيارات (`A/B/C/D`).
- كل خيار له سطر وزن واحد على الأقل.
- لا يوجد تكرار في `scenario_code`.
- استخدام كود مجموعة واحد متسق في كل الصفوف.
- استخدام أكواد الجينات المعتمدة فقط.
- النص الإنجليزي والعربي مكتمل وواضح.
