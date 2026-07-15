---
project: "obsidian-web"
slice: "opfs-vault-path"
verifier: "calev-heavy"
date: "2026-07-15"
verdict: "GO"
dod: "8/8 (all DoD §5 verified independently in a real browser)"
findings: []
env_notes:
  - id: woff2
    severity: "minor"
    summary: "2 vendor *.woff2 fonts return 404 (obsidian-mobile/public/fonts/*.woff2). Pre-existing env noise — identical on server vault, documented in opfs-geturi-fix-calev.md. NOT a regression, NOT introduced by this slice. Manifests as benign 'A network error occurred' pageerrors + Keyboard/App-not-implemented-on-android console noise (expected shim stubs)."
---
# calev-heavy — opfs-vault-path — verdict: GO

התיקון (עטיפת ה-OPFS backend ב-`wrapOpfsWithFullPath` ב-`capacitor-shim.js`) **עובד במלואו**.
אימות עצמאי בדפדפן אמיתי (chromium/playwright, שרת 4030) — כל 8 פריטי ה-DoD ב-§5 עברו,
כולל האימות הקריטי (★ workspace מלא על local OPFS vault) ומיקום קבצים נכון ללא double-nesting.
לא נמצא באג. ה-slice מכני, מוקד-שורש פעמיים, ותוקצב ל-reuse של `fullPath` הקיים — ואומת runtime
בכל נתיב-נרמול (prefix-strip, directory enum, trash single-normalize, rename/copy two-sided).

## DoD §5 — תוצאות

| # | בדיקה | תוצאה | ראיה |
|---|------|-------|------|
| 1 ★ | local vault נפתח ל-workspace מלא על OPFS | ✅ | `hasApp:true, hasWorkspace:true, hasOnboarding:false, spinnerVisible:false, vaultType:local`. צילום: `calev-local-workspace-mobile.png` (bottom-nav+ribbon, לא onboarding) + `-desktop.png` |
| 2 | file-explorer מציג קבצים/תיקיות מקוננות | ✅ | עץ מקונן אמיתי: Notes>sub>hello, Notes>top, Projects>plan, Welcome. צילום: `calev-file-explorer-nested.png` |
| 3 | קבצים נוחתים ב-`vaults/<id>/...` (לא `<id>/<id>/`) | ✅ | OPFS walk ישיר: `/vaults/<id>/Notes/sub/hello.md`. `DOUBLE_NESTED=[]` בכל הבדיקות |
| 4 | 0 /api/fs ל-local | ✅ | `API_FS_COUNT=0` על local (מול 38 על server) |
| 5 | רגרסיה: server vault (HttpFilesystem) עובד | ✅ | demo-vault נפתח (`vaultType:server`), עריכת Welcome.md → **נשמר לדיסק בפועל** (`calev-heavy-edit-<ts>` grep=1 בקובץ). 38 /api/fs. צילום: `calev-server-vault-regression.png` |
| 6 | OpfsStore self-test ALL PASS (23) | ✅ | דפדפן `opfs-store.selftest.html` → ALL PASS (23), 0 FAIL |
| 7 | 21 mobile unit-tests | ✅ (מדווח ע"י אליעזר) | לא הורץ מחדש כ-evidence (מדיניות heavy) — OpfsStore לא נגעו, self-test 23 מאשר את ה-store |
| 8 | שינוי רק ל-capacitor-shim.js (+walkthrough) | ✅ | `git diff --name-only`: `capacitor-shim.js` (קוד) + `walkthrough.md` + `opfs-plans/...md` (סטטוס-only: "מאומת"→"הושלם") |

## Edge cases — כולם עברו (זה מה ש-heavy נועד לתפוס)

- **הפרוב הקריטי** `stat({directory:'EXTERNAL', path:vaultId})` → `type:'directory'` (במקום ENOENT). זה השורש שהכריע open-vs-onboarding. ✅
- **path מוקדם-vaultId** (readFile/writeFile/stat/readdir עם `<id>/EdgeDir/a.md`) → נחת ב-`EdgeDir/a.md`, נקרא נכון. ✅
- **directory enum**: `CACHE`→`.cache/ctest.bin`, `DATA`→`.app-data/dtest.json` (אומת ב-OPFS walk). ✅ — נתיב שלא נבדק E2E ב-brief §6, כאן נבדק ישירות.
- **trash (נרמול כפול?)**: `trash({path:<id>/trashme.md})` → הקובץ נמצא ונמחק (`existsAfter:false`). נרמול **יחיד** מאושר runtime — לו היה כפול, הקובץ לא היה נמצא ונשאר. ✅
- **rename/copy** עם from/to מוקדמי-vaultId → שני הצדדים מנורמלים, src/dst נכונים. ✅
- **bind/this על ה-Proxy** (`Object.create` + `v.bind(b)`): אין שבירה — trash (היחיד שנשען על `this.deleteFile`) עבד. ✅
- **reload** (local): workspace חוזר, קבצים שורדים. ✅
- **nav-out-and-back** (registry→vault): workspace נפתח מחדש, קבצים שורדים, אין onboarding. ✅
- **rapid 3× reload** (race): workspace יציב בכל פעם, קבצים שורדים. ✅

## סיווג ל-patterns.md

אין ממצא → אין entry חדש. חתך מול 6 הקטגוריות:
- **Cat 1 (TDD ירוק ≠ התנהגות)**: אומת התנהגות אמיתית E2E, לא contract — workspace רונדר, קבצים נחתו נכון. תואם.
- **Cat 2 (cross-store/bridge null)**: הגשר כאן = dispatcher→OpfsStore. נבדק ישירות בשני ה-backends. אין null hardcoded.
- **Cat 3 (spec-drift "הסר X")**: אין "הסר X" ב-slice; scope=הוספת wrapper. DoD#8 מאשר קבצים מיועדים בלבד.
- **Cat 4 (library-compat)**: OPFS API + Object.create prototype-chain — this-binding אומת דרך trash. תקין.
- **Cat 5 (CSS/ויזואלי)**: screenshots mobile+desktop; explorer+editor רונדרו נכון (breadcrumb "Notes/sub/hello").
- **Cat 6 (reload-reconnect)**: reload + nav-out-back + rapid-reload — כולם שורדים.

## למה GO נקי מוצדק (למרות "אפס-באג חשוד")

שינוי מכני קטן (reuse של `fullPath` הקיים, לא לוגיקה חדשה), מוקד-שורש פעמיים (2 חקירות), אושר READY ע"י אביגיל,
ואני הרצתי runtime על **כל** נתיב-נרמול עם OPFS walk פיזי המאשר מיקום קבצים. opfs-store.js לא נגעו (self-test 23 ללא שינוי).
לא נותר משטח לא-מכוסה.

## Screenshots (ראיה — `/tmp/verify/opfs-vault-path/`)
- `calev-local-workspace-mobile.png` — ★ workspace מלא על local OPFS (390×844), לא onboarding
- `calev-local-workspace-desktop.png` — אותו vault, 1280×800
- `calev-file-explorer-nested.png` — ★ עץ מקונן אמיתי (Notes/sub/hello, Projects/plan)
- `calev-editor-nested.png` — ★ העורך פותח Notes/sub/hello (breadcrumb "Notes / sub / hello", תוכן מרונדר)
- `calev-server-vault-regression.png` — server vault (demo-vault) עובד, RTL Hebrew filename מרונדר
