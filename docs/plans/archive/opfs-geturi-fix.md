# Slice — opfs-geturi-fix — ‏בריף

> **‏תאריך**: 2026-07-15
> **‏סוג מסמך**: ‏בריף ביצועי לסלייס (‏תיקון באג runtime ‏שנתפס ב-preview)
> **‏סטטוס**: **הושלם** (Commits 0-2 בוצעו; ‏DoD#1-4,6-9 ✅; **DoD#5 (workspace עולה) לא הושג בבדיקת-על של אליעזר — ראה walkthrough + חריגות למטה, מועבר ל-calev-heavy**)
> **‏אימות אביגיל**: **READY** (‏דוח: `reports/obsidian-web/opfs-geturi-fix-avigail.md`)
> **Dispatch**: ‏מותר לאליעזר רק אם `אימות אביגיל = READY`.
> **Complexity**: 4/10 (verifier: **heavy** — ‏האימות האמיתי הוא render ‏מלא של Obsidian על OPFS)
> **‏תלויות (`depends_on`)**: [`opfs-store`, `opfs-wire`]
> **‏Base**: branch `opfs-wire` (‏**‏לא merged** — ‏שרשור!) — tip `fe74350`
> **‏Dev tip**: `fe74350`

---

## §0 — Pre-flight

> ‏Boilerplate: **`docs/plans/EXECUTOR_DISPATCH.md`** — ‏קרא קודם. single-branch, npm, ports 4000+, אל תהרוג BE ‏רץ, ‏אין merge/push/מחיקת worktree.

### ‏תלויות + Worktree (‏שרשור)

‏תלוי ב-`opfs-store` ‏וב-`opfs-wire` (‏שניהם לא-merged). ‏Base = branch `opfs-wire`:

```bash
cd ~/projects/obsidian-web
git worktree add .worktrees/opfs-geturi-fix -b opfs-geturi-fix opfs-wire   # ← ‏מ-opfs-wire
cd .worktrees/opfs-geturi-fix/src/server && npm install
```

### ‏הבאג — ‏מה קרה (‏נתפס ב-preview ‏עם vendor bundle ‏אמיתי)

‏כשמנסים לפתוח **local vault** ‏עם אפליקציית Obsidian ‏המלאה מרונדרת (‏אחרי `scripts/update-obsidian-mobile.js`),
‏האפליקציה **‏נתקעת ב-vault-chooser ‏ריק** — `window.app` ‏לא נוצר, `.workspace` ‏לא מופיע, ‏הספינר לא נעלם.

**‏שורש (‏אומת, ‏לא ניחוש)**: ‏ב-vault-open ‏אובסידיאן מריץ `this.uri = (await Filesystem.getUri({directory, path:''})).uri`.
‏שני נתיבי ה-getUri ‏מתנהגים שונה:

- **`HttpFilesystem.getUri`** (`capacitor-shim.js:400`) — ‏מחזיר `{uri}` ‏string ל-**‏כל** ‏path ‏בלי לגעת ב-FS. ‏לכן server vaults ‏נפתחים.
- **`OpfsStore.getUri`** (`opfs-store.js:334`) — ‏עושה `resolveParent(vaultId, '', ...)` → `parts=[]` → `name=undefined` →
  `getFileHandle(undefined)` → ‏**‏זורק NotFoundError**. ‏אין טיפול בשורש/‏תיקייה. ‏ה-vault-open ‏מת שם.

**‏באג משני**: `rethrowAsEnoent` (`opfs-store.js:113`) ‏מגן `if (e && e.code) throw e; // already a capError` —
‏אבל ל-**DOMException** ‏יש `.code` ‏**‏מספרי** (NotFoundError=8), ‏אז ה-guard ‏חושב שזה capError ‏ומדליף את ה-raw DOMException
‏במקום לעטוף ל-ENOENT.

**‏תובנת-שיטה (‏למה ה-GO ‏פספס)**: ה-self-test ‏של opfs-store ‏בדק `getUri` ‏רק על **‏קובץ** (`Notes/renamed.md`, ‏assertion 12),
‏אף פעם לא על **‏שורש `''`** — ‏שזה מה שאובסידיאן קורא בפועל. "‏ירוק ≠ ‏נכון". ‏ה-slice ‏הזה מוסיף את הכיסוי החסר.

### ‏איך להריץ + ‏לבדוק

- **‏שרת**: `cd src/server && PORT=4010 node index.js` (‏תפוס → 4011+). ‏אל תהרוג BE ‏קיים.
- **vendor bundle**: ‏ודא ש-`vendor/obsidian-mobile/` ‏קיים ב-worktree (‏אם לא → `node scripts/update-obsidian-mobile.js`).
  ‏**‏הערה**: ‏השרת מגיש גם `/worker.js`,`/sim.js`,`/i18n`,`/lib` ‏מ-`vendor/obsidian/` (‏desktop). ‏אם הם 404 ‏ב-mobile —
  ‏זו מגבלת-סביבה (‏vendor/obsidian ‏חסר), ‏**‏לא באג של ה-slice**. ‏אם צריך — `node scripts/update-obsidian.js` ‏להביא אותם.
- **‏דפדפן** (playwright/gui-host) — ‏האימות האמיתי: ‏שה-workspace ‏עולה על local vault.

### Baseline

```bash
node --test src/client-mobile/test/     # 21/21 ‏ירוק
# ‏self-test ‏בדפדפן ‏עדיין ‏ALL PASS ‏(‏לפני ‏התיקון) — ‏פרט assertion getUri-root ‏שנוסיף
```

### Reading list

- `src/client-mobile/storage/opfs-store.js` — `getUri` (334-343), `rethrowAsEnoent` (113-116), `resolveParent` (47-56), `resolveDir` (60-66), `statKind` (69+).
- `src/client-mobile/shims/capacitor-shim.js` — `HttpFilesystem.getUri` (401-406) ‏לצורך parity.
- `src/client-mobile/test/opfs-store.selftest.html` — assertion 12 (getUri).

---

## §1 — ‏מטרה

`OpfsStore.getUri` ‏**‏לעולם לא זורק** (‏כמו HttpFilesystem): ‏קובץ אמיתי → blob URL; ‏שורש/‏תיקייה/‏חסר → uri ‏סינתטי
‏לא-זורק. ‏בנוסף `rethrowAsEnoent` ‏לא מדליף DOMException. ‏תוצאה: **‏local vault ‏נפתח ל-workspace ‏מלא** ‏באפליקציית Obsidian.

---

## §2 — Scope

| ‏פיצ'ר                                                                              | ‏כן/לא                     |
| ----------------------------------------------------------------------------------- | -------------------------- |
| ‏תיקון `OpfsStore.getUri` — ‏טיפול שורש/‏תיקייה/‏חסר (‏לא זורק)                     | ✅                         |
| ‏תיקון `rethrowAsEnoent` — ‏רק string code ‏= capError                              | ✅                         |
| ‏assertions ‏ל-self-test: getUri ‏על שורש `''` ‏ועל תיקייה (‏לא זורק, ‏uri ‏string) | ✅                         |
| ‏שינוי אחר ל-opfs-store.js ‏מעבר לשני התיקונים                                      | ❌                         |
| ‏שינוי ל-capacitor-shim/boot/registry/‏שרת                                          | ❌                         |
| ‏תיקון F1 (convertFileSrc attachments)                                              | ❌ — slice ‏נפרד (opfs-ux) |

> **‏גבול**: ‏רק opfs-store.js (2 ‏פונקציות) + ה-self-test. ‏ה-slice ‏הזה **‏כן** ‏מורשה לגעת ב-opfs-store.js (‏זה תיקון שלו).

---

## §3 — ‏התיקון המדויק

### (א) `rethrowAsEnoent` (opfs-store.js:113)

```js
function rethrowAsEnoent(e, message) {
  if (e && typeof e.code === "string") throw e; // ‏capError ‏אמיתי ‏(code=string, ‏למשל 'ENOENT'); DOMException.code ‏מספרי
  throw capError("ENOENT", message);
}
```

### (ב) `OpfsStore.getUri` (opfs-store.js:334)

```js
async getUri(opts) {
  const rel = String(opts.path || '').replace(/^\/+|\/+$/g, '');   // ‏נרמל, ‏הסר '/' ‏מוביל/‏סוגר
  if (rel !== '') {
    try {
      const { parent, name } = await resolveParent(vaultId, rel, { create: false });
      const fh = await parent.getFileHandle(name, { create: false });
      return { uri: URL.createObjectURL(await fh.getFile()) };       // ‏קובץ ‏אמיתי → blob URL (‏כמו קודם)
    } catch (_) {
      // ‏תיקייה ‏או ‏חסר → ‏נפילה ‏ל-uri ‏סינתטי ‏למטה (‏לא ‏זורק, ‏כמו HttpFilesystem)
    }
  }
  return { uri: 'opfs:/vaults/' + vaultId + (rel ? '/' + rel : '/') };  // ‏שורש/‏תיקייה/‏חסר → uri ‏סינתטי
}
```

> ‏רציונל: ‏אובסידיאן מצפה מ-`getUri` ‏ל-**‏base uri ‏לא-זורק** ‏ב-vault-open. HttpFilesystem ‏אף פעם לא בודק קיום —
> ‏מחזיר string. ‏OpfsStore ‏עכשיו תואם: ‏קובץ→blob (‏ל-attachments ‏עתידיים), ‏אחרת uri ‏סינתטי. ‏ה-scheme `opfs:/`
> ‏שרירותי — ‏אובסידיאן מקבל כל string ‏שם (‏על Android ‏זה content://, ‏אצלנו <http://api/fs>, ‏עכשiu opfs:/).

---

## §4 — Commits ‏בסדר

### Commit 0 — ‏שני התיקונים ב-opfs-store.js (approach: integration)

‏החל (א) ו-(ב) ‏מ-§3. ‏שום דבר אחר.
**Verification**: `node -c src/client-mobile/storage/opfs-store.js`.

### Commit 1 — ‏כיסוי self-test ‏חסר (approach: integration)

‏ב-`opfs-store.selftest.html`, ‏אחרי assertion 12, ‏הוסף:

```js
// 13. getUri ‏על ‏שורש ‏לא ‏זורק ‏ומחזיר ‏uri ‏string (‏המקרה ‏שאובסידיאן ‏קורא ‏ב-vault-open)
const rootUri = await s.getUri({ path: "" });
assert(
  rootUri && typeof rootUri.uri === "string" && rootUri.uri.length > 0,
  'getUri("") returns non-empty uri, no throw',
);
// 14. getUri ‏על ‏תיקייה ‏לא ‏זורק
const dirUri = await s.getUri({ path: "Notes" });
assert(
  dirUri && typeof dirUri.uri === "string" && dirUri.uri.length > 0,
  "getUri(dir) returns uri, no throw",
);
// 15. getUri ‏על ‏קובץ ‏עדיין ‏blob (‏רגרסיה ‏ל-assertion 12)
const fileUri = await s.getUri({ path: "Notes/renamed.md" });
assert(fileUri.uri.startsWith("blob:"), "getUri(file) still blob: URL");
```

**Verification**: ‏פתח `opfs-store.selftest.html` ‏בדפדפן → `ALL PASS (23+)`.

### Commit 2 — walkthrough (approach: none)

‏entry ‏מתוארך ב-`docs/walkthrough.md`: ‏הבאג, ‏השורש, ‏התיקון, ‏ותובנת "self-test ‏על קובץ בלבד פספס את השורש".

---

## §5 — DoD verifiable

| #   | ‏בדיקה                                                    | ‏איך                                                                                |
| --- | --------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | `getUri({path:''})` ‏לא זורק, ‏מחזיר uri ‏string ‏לא-ריק  | self-test assertion 13                                                              |
| 2   | `getUri(dir)` ‏לא זורק                                    | assertion 14                                                                        |
| 3   | `getUri(file)` ‏עדיין blob URL (‏אין רגרסיה)              | assertion 15 + 12                                                                   |
| 4   | `rethrowAsEnoent` ‏עוטף DOMException ל-ENOENT (‏לא מדליף) | ‏עיון קוד + ‏התנהגות readFile ‏על קובץ חסר → `e.code==='ENOENT'`                    |
| 5   | **★ local vault ‏נפתח ל-workspace ‏מלא ‏על OPFS**         | ‏דפדפן: /mobile?vault=<local>, `.workspace` ‏מופיע, `window.app` ‏קיים, ‏ספינר נעלם |
| 6   | ‏עדיין 0 ‏קריאות /api/fs ‏ל-local vault                   | Network tab                                                                         |
| 7   | ‏רגרסיה: server vault ‏עדיין עובד                         | ‏פתח server vault                                                                   |
| 8   | 21 mobile unit-tests ‏ירוקים                              | `node --test src/client-mobile/test/`                                               |
| 9   | ‏שינוי רק ל-opfs-store.js + self-test (+walkthrough)      | `git diff --name-only opfs-wire..HEAD`                                              |

---

## §6 — Risks + mitigations

| ‏סיכון                                                           | ‏מיטיגציה                                                                        |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| ‏uri ‏סינתטי שובר משהו מאוחר יותר ב-Obsidian                     | calev ‏מאמת workspace ‏מלא; ‏אם נשבר במקום אחר — ‏דווח (‏ייתכן scheme ‏אחר נדרש) |
| ‏שינוי getUri ‏שובר assertion 12 ‏הקיים                          | Commit 1 assertion 15 ‏אוכף blob ‏לקובץ                                          |
| DOMException.code ‏guard ‏תופס גם capError ‏עתידי עם code ‏מספרי | ‏capError ‏תמיד string code (‏ראה capError:110) — ‏עקבי                          |
| vendor/obsidian ‏חסר → worker.js/sim.js 404 ‏חוסמים render       | §0: ‏מגבלת-סביבה; ‏אם חוסם — `node scripts/update-obsidian.js`; ‏לא באג slice    |

---

## §7 — Escalation triggers

- ‏אחרי התיקון ה-workspace ‏עדיין לא עולה (‏אולי getUri ‏הוא לא החסם היחיד — ‏דווח מה הקריאה הבאה שנכשלת).
- ‏נדרש scheme ‏אחר מ-`opfs:/` ‏כדי שאובסידיאן יקבל.
- ‏vendor/obsidian ‏חסר ‏וחוסם (‏מגבלת-סביבה — ‏דווח, ‏אל תמציא).
- ‏Testing strategy ‏סטייה.

---

## §8 — Complexity + verifier

| ‏פרמטר                                                            | ‏ניקוד |
| ----------------------------------------------------------------- | ------ |
| ‏תיקון 2 ‏פונקציות, ‏root-caused, ‏ברור                           | -2     |
| ‏כיסוי-בדיקה חדש (‏3 assertions)                                  | -1     |
| ‏אימות = **render ‏מלא של Obsidian ‏על OPFS** (‏ה-preview ‏שנחסם) | +3     |
| ‏רגרסיה dual-path                                                 | +2     |
| ‏uri scheme ‏עלול לחשוף בעיה מאוחרת                               | +1     |

**Score**: 4/10. **Tier**: `calev-heavy` — ‏האימות הקריטי הוא ה-render ‏המלא של אפליקציית Obsidian ‏על local OPFS vault
(‏בדיוק ה-preview ‏שנחסם), ‏כולל file-explorer ‏מקונן ‏ורגרסיה. ‏ודא ש-`vendor/obsidian-mobile/` ‏קיים לפני האימות.

**‏Verifier**: `Task(subagent_type="calev-heavy", ...)` — ‏מאמת DoD §5, ‏בדגש #5 (workspace ‏עולה) ‏ו-#7 (‏רגרסיה).

---

## §9 — ‏שאלות פתוחות

| #   | ‏שאלה                                    | ‏ברירת מחדל                                                   | ‏חוסם? |
| --- | ---------------------------------------- | ------------------------------------------------------------- | ------ |
| 1   | ‏scheme ל-uri ‏הסינתטי?                  | `opfs:/vaults/<id>/...` — ‏שרירותי, ‏אובסידיאן מקבל כל string | ❌     |
| 2   | ‏getUri(file) ‏עדיין blob ‏או גם סינתטי? | blob ‏לקובץ אמיתי (‏ל-attachments ‏עתידיים), ‏סינתטי אחרת     | ❌     |

---

## ‏סטיות מהתכנון (‏executor)

- **DoD#5 לא הושג בבדיקת-על של אליעזר**: התיקון (Commit 0) עובד נכון — אומת ב-trace חי בדפדפן על כל קריאות
  OpfsStore בזמן boot אמיתי (`checkPerms`, `getUri({path:'',directory:'EXTERNAL'})` ו-`getUri({directory:null,path:''})`
  שני אלה **מצליחים ולא זורקים** יותר, `stat` עוטף DOMException ל-ENOENT כראוי, `readdir('')` מצליח). **אבל** ה-workspace
  עדיין לא עולה: האפליקציה נשארת על מסך "Create a vault / Use my existing vault" (onboarding), ולחיצה על שני הכפתורים
  (כולל `force:true` ב-playwright) לא מייצרת שום קריאת OpfsStore נוספת ולא משנה DOM — נראה כמו native bridge לא-ממומש
  לזרימת ה-onboarding. תואם בדיוק את §7 escalation trigger #1 ("getUri הוא לא החסם היחיד"). מפורט ב-`docs/walkthrough.md`
  (entry "slice opfs-geturi-fix"). מועבר ל-calev-heavy לאימות עצמאי + למרדכי להחלטה על brief המשך.
- **vendor/obsidian חסר** — נוצר symlink `vendor/obsidian → obsidian-mobile` (בדיוק ה-workaround שהבריף §0 תיאר
  כמגבלת-סביבה, לא באג slice).
- **Node/npm לא זמינים בסביבת ביצוע זו** (רק `bun`) — שימוש ב-`bun install`/`bun test` במקום `npm install`/`node --test`;
  `bun.lock` שנוצר לא הוכנס ל-git.
