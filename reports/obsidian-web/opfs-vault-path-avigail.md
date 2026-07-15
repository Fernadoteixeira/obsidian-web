---
project: "obsidian-web"
slice: "opfs-vault-path"
verifier: "avigail"
date: "2026-07-15"
verdict: "READY"
findings:
  - id: 1
    severity: "minor"
    category: "naming-inconsistency"
    summary: "§3 presents two conflicting OPFS_PATH_METHODS lists (code block includes trash, final list excludes)"
    source_brief: "§3 line 102 vs line 141"
    source_code: "src/client-mobile/storage/opfs-store.js:329-331"
    cost_estimate: "0-5min"
  - id: 2
    severity: "minor"
    category: "wrong-line-number"
    summary: "HttpFilesystem.rename/copy line citations drifted (~4 lines)"
    source_brief: "§0 reading-list / §3 comment"
    source_code: "src/client-mobile/shims/capacitor-shim.js:348-350,367-369"
    cost_estimate: "0min"
---

# Plan Verification — opfs-vault-path

> **Brief**: docs/plans/opfs-vault-path.md
> **Base tip**: bcd9b98 (branch opfs-geturi-fix, worktree .worktrees/opfs-geturi-fix)
> **Verdict**: ✅ READY
> **אומדן זמן אליעזר confusion אם לא תוקן**: ~2 דק' (רק אם יקרא את שני הרשימות ויתלבט)

הבריף יוצא-דופן במידת הקפדנות — כל 7 נקודות-האימות שמרדכי סימנה נבדקו מול הקוד האמיתי
ב-.worktrees/opfs-geturi-fix ו**כולן מאמתות את הגישה**. אין blocker, אין regression, אין type-error.
שני ממצאים בלבד, שניהם 🟢 cosmetic.

## בעיות שנמצאו

### 🔴 Blocker / Regression risk

(אין)

### 🟡 Confusion / Type error / Outdated

(אין)

### 🟢 Minor

| # | בעיה | מקור | הצעה |
|---|------|------|------|
| 1 | §3 מציג **שתי רשימות סותרות** ל-`OPFS_PATH_METHODS`: בלוק-הקוד (line 102) כולל `'trash'`, והרשימה-הסופית (line 141) מסירה אותו. אליעזר שמעתיק את בלוק-הקוד verbatim יקבל trash-ברשימה. **פונקציונלית שתי הגרסאות בטוחות** (ראה ניתוח למטה — נרמול יחיד בשני המקרים), אבל הסתירה מזמינה בלבול. | brief §3 line 102 מול line 141; `opfs-store.js:329-331` | מרדכי — לאחד: להכניס את הרשימה-הסופית (ללא trash) ישירות לבלוק-הקוד, ולמחוק את ההערה המתקנת בשורות 132-141. |
| 2 | ציטוטי מספרי-שורות של `HttpFilesystem.rename`/`copy` סטו: הבריף מצטט 344-346 / 363-366, בפועל rename ב-348-350, copy ב-367-369. ה-anchor (`HttpFilesystem.rename`/`copy` דפוס `fullPath({path:opts.from...})` + `toDirectory||directory`) קיים ונכון. | brief §0 reading-list + §3; `capacitor-shim.js:348-350,367-369` | cosmetic — לעגן ב-pattern במקום מספר. אל תבזבז זמן על אימות המספר. |

## Spot-check שעבר (אומת מול קוד אמיתי)

- ✅ `fullPath` — `capacitor-shim.js:127-141` (ציטוט מדויק). עושה `resolvePrefix(directory)` + הסרת vaultId: `p===vaultId → ''`, `p.startsWith(vaultId+'/') → slice`. אמת מדויק. (בדיקה 1)
- ✅ `resolvePrefix` — line 112 (בריף ציטט 110-125; קרוב). ממפה EXTERNAL/DOCUMENTS→'', CACHE→'.cache/', DATA/LIBRARY→'.app-data/'. אמת.
- ✅ `fsBackend()` line 532, `const Filesystem = new Proxy` line 541, `window.__owLocalFs = ...makeStore(...)` line 535 — כל המיקומים ~532-551 מדויקים. (בדיקה 2)
- ✅ `getVaultId` line 96 — בתוך אותו IIFE-scope, נגיש ל-wrapper וקרוא ע"י `fullPath` ב-runtime.
- ✅ **בדיקה 3 (נרמול כפול / trash)**: `opfs-store.js:329-331` — `trash` אכן עושה `return this.deleteFile(opts)`. ההסקה נכונה, וחזקה יותר ממה שהבריף טוען:
  - **trash מחוץ לרשימה (הסופי)**: `Filesystem.trash(raw)` → Proxy `v.bind(b)` עם b=wrapped → `this=wrapped` → `wrapped.deleteFile(raw)` (arrow-override מנרמל) → **נרמול יחיד**. ✅
  - **trash בתוך הרשימה (בלוק-הקוד השגוי)**: `wrapped.trash = (o)=>store.trash({...o, path:fullPath(o)})`. כשקורא `store.trash(x)` → `this=store` → `store.deleteFile(x)` (raw), ו-x.path כבר מנורמל → **גם כאן נרמול יחיד**. ✅
  - מסקנה: אין תרחיש double-normalization בשום קונפיגורציה. הפחד של הבריף (§6 שורה 178) לא מדויק בסיבתיות, אך ההחלטה הסופית (להוציא trash) בטוחה. Finding #1 נשאר cosmetic בלבד.
- ✅ **בדיקה 4 (bind מול Object.create)**: ה-Proxy עושה `v.bind(b)` עם b=wrapped. overrides הם arrow-functions → מתעלמים מ-bind (לא מזיק). passthrough (`watchAndStatAll`/`startWatch`/`stopWatch`/`addListener`/`setTimes`) → `this=wrapped`, אך אף אחד מהם לא נשען על `this`. אין בעיית this. ✅
- ✅ **בדיקה 5 (כיסוי הרשימה)**: מיפוי מלא של מתודות OpfsStore שמקבלות `opts.path`: readFile/writeFile/appendFile/deleteFile/mkdir/rmdir/readdir/stat/getUri — כולן ברשימה הסופית. rename/copy (from/to) בטיפול נפרד. trash → passthrough→deleteFile. `setTimes`/`open`/`verifyIcloud`/`checkPerms`/`watchAndStatAll` — no-op או ללא path. **הרשימה מכסה בדיוק, לא יותר.** ✅
- ✅ **בדיקה 5b (getUri convergence)**: `Filesystem.getUri({directory:'EXTERNAL', path:vaultId})` → fullPath → prefix='' + path='' → `store.getUri({path:''})` → `rel===''` → synthetic `opfs:/vaults/<id>/` (opfs-store.js:334-351). מתלכד עם תיקון opfs-geturi-fix ה-root-handling. subfile אמיתי → strip → blob-url. ✅
- ✅ **בדיקה 6 (rename/copy pattern)**: הדפוס בבריף (`from: fullPath({path:opts.from, directory:opts.directory})`, `to: fullPath({path:opts.to, directory:opts.toDirectory||opts.directory})`) **זהה מילה-במילה** ל-`HttpFilesystem.rename` (348-350) ו-`copy` (367-369). store.rename/copy משתמשים ב-closure helpers (copyPath/statKind/removePath) על from/to המנורמלים. ✅
- ✅ **בדיקה 7 (הכי קריטי — closure reliance)**: כל מתודות OpfsStore נשענות על **closures** מעל `vaultId` + helpers פנימיים (`resolveParent`/`resolveDir`/`vaultDir`/`statKind`/`readFileRaw`/`writeFileRaw`/`copyPath`/`removePath`) — כולם נלכדים ב-lexical scope של `makeStore`, **בלתי-תלויים ב-`this`**. `Object.create(store)` + override **לא שובר אף מתודה**. היחיד שנשען על `this` הוא `trash` — ומטופל נכון (בדיקה 3). ✅
- ✅ **בדיקה 8 (depends_on)**: §0 מצהיר `depends_on: [opfs-store, opfs-wire, opfs-geturi-fix]`, Base=opfs-geturi-fix@bcd9b98. עקבי. אין state.json בפרויקט (התלות ב-§0). לא ריק. ✅
- ✅ probe-fix: `stat({directory:'EXTERNAL', path:vaultId})` → fullPath → `''` → `store.stat({path:''})` → `{type:'directory'}` (opfs-store.js:293-294) → window.app נוצר → workspace. מתאים לתזה. ✅
- ✅ scope: opfs-store.js **לא נוגעים** — כל ה-wrapper ב-capacitor-shim.js. נקי.

## Verdict

✅ **READY** — העבר לאליעזר. אין blocker/regression/type-error. שני ממצאי-cosmetic בלבד:
- Finding #1 (רשימות סותרות) — מומלץ שמרדכי תאחד את בלוק-הקוד לרשימה-הסופית לפני dispatch כדי למנוע בלבול-רגעי, אך **בטוח פונקציונלית גם אם לא** (נרמול יחיד בשתי הגרסאות).
- Finding #2 (מספרי-שורה) — trivial, לעגן ב-pattern.

הערה: זהו קובץ JS (ללא TypeScript strict), אז אין בדיקת type — רק `node -c` syntax check שהבריף כבר כולל (§4 Commit 0).
