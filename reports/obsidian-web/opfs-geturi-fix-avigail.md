---
project: "obsidian-web"
slice: "opfs-geturi-fix"
verifier: "avigail"
date: "2026-07-15"
verdict: "READY"
findings:
  - id: 1
    severity: "minor"
    category: "wrong-line-number"
    summary: "capError cited as opfs-store.js:110 but function is at 107 (e.code set at 109)"
    source_brief: "§3(א) comment + §0 reading list + §6 mitigation"
    source_code: "src/client-mobile/storage/opfs-store.js:107"
    cost_estimate: "<1min"
  - id: 2
    severity: "minor"
    category: "wrong-line-number"
    summary: "HttpFilesystem.getUri cited as capacitor-shim.js:400 but is at 401"
    source_brief: "§0 background + §0 reading list"
    source_code: "src/client-mobile/shims/capacitor-shim.js:401"
    cost_estimate: "<1min"
  - id: 3
    severity: "confusion"
    category: "unique"
    summary: "finding-6 assumption (getUri is the only vault-open blocker) — verified as well-supported, flag for calev residual F1/resource-uri risk"
    source_brief: "§6 risks + §7 escalation + §9 Q1"
    source_code: "vendor/obsidian-mobile/app.js (CapacitorFileSystemAdapter.init)"
    cost_estimate: "0min (already flagged by brief)"
---

# Plan Verification — opfs-geturi-fix

> **Brief**: docs/plans/opfs-geturi-fix.md
> **Base tip**: fe74350 (branch opfs-wire, worktree .worktrees/opfs-wire)
> **Verdict**: ✅ READY
> **אומדן זמן אליעזר confusion אם לא תוקן**: ~2 דק' (רק line-number cosmetics)

הבריף root-caused, מדויק, וכל 6 הclaims אומתו מול הקוד האמיתי + vendor bundle אמיתי. אין blocker, אין regression, אין dropped-branch. הפרויקט plain-JS (`node -c`), אין strict-TS → אין type-error findings.

## בעיות שנמצאו

### 🔴 Blocker / Regression risk

(אין)

### 🟡 Confusion / Type error / Outdated

| # | בעיה | מקור | הצעה |
|---|------|------|------|
| 3 | finding-6 ("האם getUri הוא החסם היחיד ב-vault-open") — הבריף מסמן אותו כהנחה. אימות: ב-`CapacitorFileSystemAdapter.init()` בvendor רצה **קריאה אחת** `getUri({directory:this.dir,path:""})` שסוגרת את `this.uri` — זה בדיוק המקום שנחסם. getUri השני בbundle הוא `getUri({path:appId+"/tab-preview",directory:M.Cache})` — **directory שונה (Cache), לא vault-FS**. שאר פעולות ה-adapter (list/stat) ממופות למתודות OpfsStore שעובדות (מכוסות ב-self-test). לכן ההנחה **נתמכת** — התיקון מספיק כדי ש-init יצליח וה-workspace יעלה. | brief §6/§7/§9 Q1 / vendor/obsidian-mobile/app.js | אין חסימה. calev-heavy יאמת render מלא (DoD #5). סיכון שאריתי היחיד: uri סינתטי `opfs:/` שובר resource/attachment URLs מאוחר יותר — אבל זה F1 (convertFileSrc) שהבריף §2 דוחה במפורש ל-opfs-ux, ולא חוסם הופעת workspace. |

### 🟢 Minor

| # | בעיה | מקור |
|---|------|------|
| 1 | `capError` מצוטט כ-`opfs-store.js:110` (§3א comment, §6 mitigation, §0 reading list). בפועל הפונקציה ב-107, `e.code = code` ב-109. ה-anchor `capError` קיים וחד-ערכי — הטענה עצמה ("code תמיד string") **נכונה**. | brief §3(א)/§6/§0 |
| 2 | `HttpFilesystem.getUri` מצוטט כ-`capacitor-shim.js:400`, בפועל ב-401. anchor קיים וחד-ערכי. | brief §0 |

> הערת check-4: הבריף מצמיד לכל מספר-שורה גם שם-symbol (anchor), לכן ה-drift לא יבלבל את אליעזר. המלצה למרדכי לעתיד: עגני ב-symbol בלבד. **אל תבזבזו זמן על תיקון המספרים** — cosmetic.

## Spot-check שעבר (אימות מלא)

- ✅ **claim 1** — `OpfsStore.getUri` ב-`opfs-store.js:334` עושה `resolveParent(vaultId, opts.path)` ואז `getFileHandle(name)`. על `path=''` אכן זורק. אומת.
- ✅ **claim 5** — `resolveParent` (`opfs-store.js:47`): `split('/').filter(Boolean)` → `parts=[]` ל-`path=''`, `parts.pop()` → `name=undefined`. אומת. `getFileHandle(undefined)` → זורק. (בין אם TypeError או NotFoundError — getUri זורק בשני המקרים; זו הליבה.)
- ✅ **claim 2** — `rethrowAsEnoent` ב-`opfs-store.js:113`: `if (e && e.code) throw e`. DOMException `NotFoundError` code=8 (numeric truthy) → מדליף raw. `capError` (107-109) מגדיר `e.code = code` (string תמיד). התיקון `typeof e.code === 'string'` נכון. אומת. (הערה: זהו תיקון defensive משני — התיקון העיקרי הוא getUri לא-זורק.)
- ✅ **claim 3** — `HttpFilesystem.getUri` ב-`capacitor-shim.js:401` מחזיר `{uri: location.origin + '/api/fs/read?...'}` string לכל path בלי לגעת ב-FS. זו הסיבה ש-server vaults נפתחים. אומת (parity target תקף).
- ✅ **claim 4** — self-test assertion 12 (`opfs-store.selftest.html:130-132`) בודק getUri רק על קובץ `Notes/renamed.md`, אף פעם לא על שורש `''`. הפער אומת → "ירוק ≠ נכון". Commit 1 (assertions 13/14/15) סוגר אותו; מצב הטסט ('Notes' dir + 'Notes/renamed.md' קיימים בנקודת ההוספה) תומך ב-assertions החדשים.
- ✅ **claim 6 (vendor אמיתי)** — `getUri({directory:this.dir,path:""})` קיים ב-`vendor/obsidian-mobile/app.js` בתוך `CapacitorFileSystemAdapter.init()`, מציב `this.uri`. תרחיש הבאג אומת מול ה-bundle האמיתי.
- ✅ **§3(ב) pseudo-code** — לא מחסיר branch מהותי מול הקוד הקיים: file→blob נשמר (assertion 12 + 15 לא נשברים), else→synthetic במקום throw (זו כל המטרה, parity ל-HttpFilesystem). `vaultId` זמין ב-closure של makeStore. אין callers פנימיים אחרים ל-getUri (grep) → הפיכתו ללא-זורק לא שוברת קוד קיים.
- ✅ **check 8 (depends_on)** — `depends_on: [opfs-store, opfs-wire]` (שורה 9) עקבי; Base = branch `opfs-wire` @ fe74350; `opfs-store.js` קיים ב-worktree הבסיס (נקרא ישירות). §0 מפרט את השרשור. תקין.

## Verdict

✅ **READY** — הבריף טכנית-נכון. כל ה-symbols/anchors קיימים, ה-pseudo-code לא מחסיר branches, ה-dual-path regression מכוסה (assertion 15), depends_on עקבי, והתיקון אומת מול ה-vendor bundle האמיתי שבו נתפס הבאג. הממצאים היחידים הם 2 סטיות מספר-שורה cosmetic (המשולבות עם anchor שמי → לא מבלבלות) + הבהרה שהנחת finding-6 נתמכת. **העבר לאליעזר.** calev-heavy יאמת DoD #5 (workspace עולה) + #7 (regression server-vault) ב-render מלא.
