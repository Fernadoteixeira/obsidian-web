---
project: "obsidian-web"
slice: "opfs-store"
verifier: "avigail"
date: "2026-07-15"
round: 2
verdict: "READY"
findings:
  - id: 1
    severity: "minor"
    category: "unique"
    summary: "getUri surface divergence: shim returns HTTP url (location.origin + /api/fs/read), OPFS returns blob: url — deliberate design, documented in §4/§9, not a defect"
    source_brief: "§4 getUri row / §1 same-surface claim"
    source_code: "src/client-mobile/shims/capacitor-shim.js:394"
    cost_estimate: "0min"
---

# Plan Verification (round 2) — opfs-store

> **Brief**: docs/plans/opfs-store.md
> **Base tip**: c784f6a
> **Verdict**: ✅ READY
> **אומדן זמן אליעזר confusion אם לא תוקן**: 0 דק'

## מטרת הסבב

סבב 1 החזיר USABLE-AFTER-FIX עם 3 ממצאים. סבב זה מאמת שהתיקונים נכונים+מספיקים,
שלא נפתחה בעיה חדשה, ובפרט שני החששות שהועלו: assertion 11 (appendFile / OPFS API)
ו-assertion 12 (getUri / fetch(blob:) בדפדפן).

## אימות התיקונים משבר 1

### ✅ תיקון 1 — baseline 14→21 (היה 🟡 wrong-count)

- ספירת `test()`/`it()` בפועל: bootstrap-lookup=9, requesturl-base64=7, cache-invalidation=5 → **סה"כ 21**. תואם.
- כל 5 המופעים בבריף אומתו: שורות 49, 56, 311, 333, 360 — כולם `21`.
- אין שריד `14` בבריף. הפירוק בשורה 56 (`9 + 7 + 5`) נכון.
- (הערת env: בסביבת האימות שלי אין `node` אמיתי — רק `bun` ממופה כ-node — לכן לא הרצתי `node --test`.
  הספירה אומתה סטטית ב-grep. זו מגבלת סביבה שלי, לא בעיית בריף; ל-executor יש Node אמיתי.)

### ✅ תיקון 2 — appendFile + getUri assertions (היה 🟡 missing-assertion)

- **assertion 11** (§4 שורות 268-274) קיים; DoD §5 row 8 נוסף; §9 Q2 הוכרע ("לא עוד פתוח").
- **assertion 12** (§4 שורות 276-279) קיים; DoD §5 row 9 נוסף.
- סמנטיקת appendFile קובעה חד-משמעית ב-§4 (read→concat→write→close) ובחוזה-המתודה. עקבי.

### ✅ תיקון 3 — line ref Filesystem 178-505→178-514 (היה 🟢 wrong-line-number)

- אומת: `const Filesystem = {` בשורה 178; ה-`};` הסוגר בשורה 514. תואם.
- אין שריד `178-505`. גם ההפניה `capacitor-shim:385-387` (setTimes/verifyIcloud/open) אומתה נכונה.

## בדיקת שני החששות (regressions חדשים?)

### assertion 11 — appendFile מבחינת OPFS API — ✅ תקין

- הגישה בבריף (read-existing → concat → write → close) **נכונה ל-OPFS**: `createWritable()`
  ברירת-מחדל היא `keepExistingData:false` (מקצץ לריק), ולכן חובה לקרוא את הבייטים הקיימים
  ולכתוב את הכל מחדש — בדיוק מה שהבריף מורה. החלופה `createWritable({keepExistingData:true})`
  + `write({type:'write',position:size})` שהבריף מזכיר גם היא חוקית ל-OPFS.
- ה-assertion עצמו נכון-מתמטית: הוא משווה ל-`btoa('AAABBB')` (base64 של הבייטים המשורשרים),
  **ולא** ל-`btoa('AAA')+btoa('BBB')` (שרשור מחרוזות-base64 שהיה שגוי כשאורך לא כפולה של 3).
  זה בדיוק מה ש-`readFile` ללא encoding מחזיר (base64 של כל בייטי הקובץ) → byte-append מאומת נכון.

### assertion 12 — getUri / fetch(blob:) בדפדפן — ✅ עובד

- `URL.createObjectURL(file)` על `File` שמוחזר מ-`FileSystemFileHandle.getFile()` מייצר blob: URL תקין.
- `fetch(blobUrl).then(r=>r.text())` **נתמך בכל הדפדפנים המודרניים** (Chrome/Firefox/Safari) — זהו נתיב סטנדרטי.
  ה-assertion יעבור בסביבת ה-self-test.

## 🟢 הערה מינורית (לא חוסמת, לידיעת מרדכי)

- **getUri surface divergence**: capacitor-shim מחזיר URL של HTTP (`location.origin + /api/fs/read?...`,
  שורה 394), ואילו מודול ה-OPFS מחזיר `blob:` URL. §1 מצהיר "אותן צורות" ל-Filesystem.
  ערך ה-`uri` שונה סמנטית (http לעומת blob). זו **החלטת-תכנון מכוונת ומתועדת** (§4 חוזה getUri + §9),
  והצריכה בפועל היא ב-slice `opfs-wire` הנפרד. ה-self-test עקבי-פנימית. **לא defect ולא חוסם** —
  רק ראוי שמרדכי תהיה מודעת שאם צרכן כלשהו מסתמך על uri כ-URL עמיד (blob נמחק ב-page-unload), זה יטופל ב-opfs-wire.

## Spot-check שעבר (לא מצא בעיה)

- ✅ `arrayBufferToBase64` @ capacitor-shim.js:86 — אומת (ref בבריף §Reading-list נכון)
- ✅ `base64ToArrayBuffer` @ capacitor-shim.js:78 — אומת
- ✅ `capError` @ capacitor-shim.js:143 — אומת
- ✅ `const Filesystem` @ 178, סגירה @ 514 — אומת
- ✅ stubs setTimes/verifyIcloud/open @ 385-387 — אומת
- ✅ `appendFile` / `getUri` קיימים בשים כפני-שטח שצריך לשקף (20-21, 235, 394) — אומת
- ✅ depends_on: `[]` — נכון; המודול greenfield, 2 קבצים חדשים בלבד, 0 עריכות לקוד קיים (§0/§2). עקבי.
- ✅ נתיבי קבצים חדשים: `src/client-mobile/storage/` (חדש) + `src/client-mobile/test/` (קיים) — סבירים; אין התנגשות שם.

## Verdict

**✅ READY** — כל 3 התיקונים מסבב 1 נכונים ומספיקים. שני החששות שנבדקו (appendFile OPFS-API,
getUri fetch(blob:)) תקינים. לא נפתחה בעיה חדשה חוסמת. הערה 🟢 יחידה היא החלטת-תכנון מתועדת, לא defect.
מותר dispatch לאליעזר.
