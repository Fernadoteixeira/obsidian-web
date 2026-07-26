# Slice — opfs-vault-path — ‏בריף

> **‏תאריך**: 2026-07-15
> **‏סוג מסמך**: ‏בריף ביצועי (‏תיקון שורש שיטתי — ‏parity ‏של חוזה-נתיבים בשכבת ה-dispatcher)
> **‏סטטוס**: **‏הושלם** (Commits 0-1, ‏branch `opfs-vault-path`) — ‏ראו `docs/walkthrough.md` ‏entry `2026-07-15 — slice opfs-vault-path`
> **‏אימות אביגיל**: **READY** (‏דוח: `reports/obsidian-web/opfs-vault-path-avigail.md`)
> **Dispatch**: ‏מותר לאליעזר רק אם `אימות אביגיל = READY`.
> **Complexity**: 5/10 (verifier: **heavy** — ‏render ‏מלא של Obsidian על OPFS)
> **‏תלויות (`depends_on`)**: [`opfs-store`, `opfs-wire`, `opfs-geturi-fix`]
> **‏Base**: branch `opfs-geturi-fix` (‏**‏לא merged** — ‏שרשור!) — tip `bcd9b98`
> **‏Dev tip**: `bcd9b98`

---

## §0 — Pre-flight

> Boilerplate: **`docs/plans/EXECUTOR_DISPATCH.md`**. single-branch, npm(/bun), ports 4000+, אל תהרוג BE, אין merge/push/מחיקת worktree.

### ‏תלויות + Worktree (‏שרשור)

```bash
cd ~/projects/obsidian-web
git worktree add .worktrees/opfs-vault-path -b opfs-vault-path opfs-geturi-fix   # ← ‏מ-opfs-geturi-fix
cd .worktrees/opfs-vault-path/src/server && npm install    # ‏(‏או bun install)
```

### ‏הבאג — ‏מה קרה (‏מוכח ‏ע"י **‏שתי** ‏חקירות + fix-simulation)

‏אחרי תיקון getUri (opfs-geturi-fix), local vault ‏עדיין **‏נתקע על onboarding**. ‏שורש מוכח:
‏Obsidian mobile ‏משתמש ב-**vaultId ‏כ-base-path** ‏ומקדים אותו לכל קריאת FS. ‏ב-vault-open ‏הוא קורא
`stat({directory:'EXTERNAL', path: vaultId})` — ‏זו **‏הקריאה היחידה** ‏שמכריעה open-vs-onboarding:

- **server**: `HttpFilesystem` ‏מריץ כל opts ‏דרך `fullPath()` (`capacitor-shim.js:127-141`) שמסיר את קידומת ה-vaultId → `stat('')` → `{directory}` → `window.app` ‏נוצר → workspace ✅
- **local**: `OpfsStore.stat({path: vaultId})` ‏מפרש כ-`vaults/<id>/<id>` → ‏לא קיים → ENOENT → `window.app` ‏לא נוצר → **onboarding** ❌

‏ה-onboarding ‏הוא **‏תסמין** (‏fallback ‏דיפולטי כשלא נבחר vault) — ‏הבאג הוא שלא הגענו ל-`window.app` ‏מלכתחילה.

**‏הוכחה (‏2 ‏fix-simulations ‏עצמאיות)**: ‏הזרקת נרמול-נתיב (`resolvePrefix(directory)` + ‏הסרת vaultId prefix)
‏לפני ה-OPFS backend → **`hasWorkspace:true, hasApp:true, hasOnboarding:false`**, ‏כתיבת `Notes/sub/hello.md`
‏נחתה נכון ב-`vaults/<id>/Notes/sub/hello.md` (‏**‏לא** double-nested ‏תחת `<id>/<id>/`), ‏הכל על OPFS, 0 /api/fs.
‏ראיות: `/tmp/verify/opfs-onboarding/local-with-fix.png`, `/tmp/verify/opfs-geturi-fix/local-vault-PATCHED-workspace.png`.

**‏קריטי — ‏רחב מה-probe**: ‏**‏כל** ‏פעולות ה-FS ‏אחרי הפתיחה מגיעות עם קידומת vaultId (‏ה-adapter base = vaultId).
‏בלי הנרמול, ‏קבצים היו נכתבים ל-`vaults/<id>/<id>/...`. ‏הנרמול היחיד סוגר גם את ה-probe וגם את מיקום כל הקבצים.

### ‏החלטת מיקום — ‏ב-dispatcher, ‏לא ב-OpfsStore (‏החלטת מרדכי)

‏התיקון ב-**`capacitor-shim.js` (‏ה-Proxy dispatcher)**, ‏לא ב-`opfs-store.js`. ‏רציונל:

- ‏vaultId-as-basepath ‏ו-`directory` enum ‏הם דאגות של **‏שכבת ה-Capacitor-adapter**, ‏לא של OpfsStore
  (‏שחוזהו המפורש בראש הקובץ: "keys are vault-relative"). ‏חשוב ל-LiveSync/local-vaults ‏העתידי שבו OpfsStore ‏נקרא ישירות.
- `HttpFilesystem` ‏כבר פותר את זה עם `fullPath()` — ‏ה-dispatcher ‏צריך לתת ל-OpfsStore path ‏מנורמל **‏זהה**.
- ‏שימוש חוזר ב-`fullPath()` ‏הקיים = single-source-of-truth, ‏בלי שכפול לוגיקה שעלול לסטות.
- **‏שומר את `opfs-store.js` ‏ללא שינוי** (‏ה-GO ‏שלו נשמר; ‏getUri ‏שכבר תוקן ב-opfs-geturi-fix ‏נשאר — ‏זו דאגה vault-relative ‏לגיטימית).

### ‏vendor + ‏הרצה

- **‏שרת**: `cd src/server && PORT=4030 node index.js` (‏תפוס → 4031+). ‏אל תהרוג BE.
- **vendor**: ‏ודא `vendor/obsidian-mobile/` (`cp -r ../opfs-geturi-fix/vendor .` ‏אם קיים, ‏אחרת `node scripts/update-obsidian-mobile.js`).
  ‏אם `/worker.js`,`/sim.js` 404 → `ln -s obsidian-mobile vendor/obsidian` (‏workaround ‏סביבתי).
- **‏דפדפן** — ‏האימות: ‏workspace ‏עולה על local vault.

### Baseline

```bash
node --test src/client-mobile/test/     # 21/21 ‏ירוק
# ‏self-test ‏בדפדפן → ALL PASS (23) — ‏לא ‏אמור ‏להשתנות (‏OpfsStore ‏לא ‏נוגעים)
```

### Reading list — ‏קריטי

- **`src/client-mobile/shims/capacitor-shim.js`**: `resolvePrefix` (110-125), `fullPath` (127-141) — **‏הפונקציה לשימוש-חוזר**;
  `HttpFilesystem.rename/copy` (348-350, 367-369) — ‏דוגמת נרמול from/to; `fsBackend()` + `const Filesystem = new Proxy` (~532-551).
- `src/client-mobile/storage/opfs-store.js` — ‏פני-השטח (‏**‏לא נוגעים** — ‏רק מבינים מה מקבל).
- calev reports: `reports/obsidian-web/opfs-geturi-fix-calev.md` + ‏חקירות ב-`/tmp/verify/opfs-onboarding/`.

---

## §1 — ‏מטרה

‏ה-dispatcher ‏מנרמל כל `opts` **‏זהה ל-`fullPath`** ‏לפני האצלה ל-OpfsStore: (‏א) ‏מסיר קידומת vaultId,
(‏ב) ‏מפענח directory-prefix (CACHE→`.cache/`, DATA/LIBRARY→`.app-data/`). ‏OpfsStore ‏מקבל path ‏vault-relative ‏נקי.
‏תוצאה: **‏local vault ‏נפתח ל-workspace ‏מלא** ‏על OPFS, ‏וכל הקבצים נוחתים במיקום הנכון.

---

## §2 — Scope

| ‏פיצ'ר                                                           | ‏כן/לא                   |
| ---------------------------------------------------------------- | ------------------------ |
| ‏עטיפת ה-OPFS backend ב-`fsBackend()` ‏עם נרמול `fullPath`       | ✅                       |
| ‏נרמול path ‏לכל מתודה עם `opts.path`, ‏ו-from/to ‏ל-rename/copy | ✅                       |
| ‏אימות render ‏מלא (E2E)                                         | ✅ (calev)               |
| ‏שינוי ל-`opfs-store.js`                                         | ❌ (‏נשאר GO ‏ללא שינוי) |
| ‏שינוי ל-`HttpFilesystem` / boot / registry / ‏שרת               | ❌                       |

> **‏גבול**: ‏רק `capacitor-shim.js` (‏עטיפת ה-OPFS backend ב-fsBackend) + walkthrough. ‏**‏לא נוגעים ב-opfs-store.js.**

---

## §3 — ‏התיקון המדויק

‏ב-`capacitor-shim.js`, ‏ב-`fsBackend()` (‏שם נוצר `window.__owLocalFs = window.__owOpfsStore.makeStore(...)`),
‏עטוף את ה-store ‏המוחזר ב-**‏wrapper ‏שמנרמל opts ‏דרך `fullPath`** ‏לפני האצלה:

```js
// ‏מתודות ‏שמקבלות ‏opts.path ‏(‏נרמל ‏path ‏יחיד). ‏שים ‏לב: ‏trash ‏**‏לא** ‏כאן — ‏הוא ‏מאציל ‏ל-deleteFile ‏המנורמל.
const OPFS_PATH_METHODS = [
  "readFile",
  "writeFile",
  "appendFile",
  "deleteFile",
  "mkdir",
  "rmdir",
  "readdir",
  "stat",
  "getUri",
];

function wrapOpfsWithFullPath(store) {
  const wrapped = Object.create(store); // ‏passthrough ‏לכל ‏השאר (watchAndStatAll, startWatch, stopWatch, addListener, setTimes, ...)
  for (const m of OPFS_PATH_METHODS) {
    if (typeof store[m] !== "function") continue;
    wrapped[m] = (opts) =>
      store[m](Object.assign({}, opts, { path: fullPath(opts) }));
  }
  // rename/copy — ‏נרמל ‏שני ‏הצדדים (‏כמו HttpFilesystem:348-350, 367-369)
  if (typeof store.rename === "function") {
    wrapped.rename = (opts) =>
      store.rename(
        Object.assign({}, opts, {
          from: fullPath({ path: opts.from, directory: opts.directory }),
          to: fullPath({
            path: opts.to,
            directory: opts.toDirectory || opts.directory,
          }),
        }),
      );
  }
  if (typeof store.copy === "function") {
    wrapped.copy = (opts) =>
      store.copy(
        Object.assign({}, opts, {
          from: fullPath({ path: opts.from, directory: opts.directory }),
          to: fullPath({
            path: opts.to,
            directory: opts.toDirectory || opts.directory,
          }),
        }),
      );
  }
  return wrapped;
}
```

‏ואז ב-`fsBackend()`:

```js
if (!window.__owLocalFs) {
  window.__owLocalFs = wrapOpfsWithFullPath(
    window.__owOpfsStore.makeStore(window.__owVaultId || getVaultId()),
  );
}
```

> ⚠️ **bind/this**: ה-Proxy ‏הקיים עושה `v.bind(b)`. ‏עם `Object.create(store)`, `wrapped.trash` ‏(‏passthrough) ‏קורא
> `this.deleteFile` — ‏`this`=wrapped → `wrapped.deleteFile` (‏המנורמל) → OK, ‏נרמול פעם אחת. ‏ודא ש-trash ‏**‏לא** ‏ברשימת
> OPFS_PATH_METHODS ‏(‏הוא מאציל ל-deleteFile ‏שמנרמל) — **‏אחרת נרמול כפול**. ‏[‏הסר trash ‏מהרשימה אם deleteFile ‏מנרמל].
> ‏תיקון: ‏השאר trash ‏**‏מחוץ** ‏ל-OPFS_PATH_METHODS; ‏הוא passthrough ‏שקורא deleteFile ‏המנורמל.

> ⚠️ ‏`watchAndStatAll` — ‏לא מקבל path, ‏passthrough (‏walk ‏מ-root). ‏OK.
> ⚠️ ‏העטיפה **‏רק ל-OPFS**; server ‏ממשיך ל-`HttpFilesystem` ‏שמנרמל בעצמו — ‏אין כפילות.

> **‏trash**: ‏כבר מוסר מהרשימה למעלה — ‏passthrough (‏Object.create) ‏שקורא `this.deleteFile` ‏המנורמל. ‏אין לו entry ‏משלו.

---

## §4 — Commits ‏בסדר

### Commit 0 — wrapper + ‏החלה ב-fsBackend (approach: integration)

‏החל §3. `node -c src/client-mobile/shims/capacitor-shim.js`.

### Commit 1 — walkthrough (approach: none)

‏entry: ‏השורש (vaultId-prefix parity בשכבת ה-adapter), ‏למה ב-dispatcher ‏ולא ב-OpfsStore, ‏ה-fix-simulation,
‏ותובנת קטגוריה-1 (‏נתיב vaultId-prefixed לא נבדק — ‏גרם ל-2 ‏באגים).

> ‏**‏הערה על בדיקה**: ‏העטיפה יושבת ב-capacitor-shim (IIFE, ‏תלוי window globals) — ‏קשה ל-unit-test. ‏האימות
> ‏הקריטי הוא **calev-heavy E2E** (‏workspace ‏עולה). ‏ה-self-test ‏של OpfsStore (23) ‏נשאר כמות שהוא ‏ומאמת שה-store ‏עצמו לא נשבר.

---

## §5 — DoD verifiable

| #   | ‏בדיקה                                                 | ‏איך                                                                                |
| --- | ------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| 1   | **★ local vault ‏נפתח ל-workspace ‏מלא ‏על OPFS**      | ‏דפדפן: `.workspace` ‏מופיע, `window.app` ‏קיים, ‏ספינר נעלם, ‏onboarding ‏לא מופיע |
| 2   | file-explorer ‏מציג קבצים/תיקיות מקוננות               | ‏צור Notes/sub/x.md → ‏נראה ב-explorer                                              |
| 3   | ‏קבצים נוחתים ב-`vaults/<id>/...` (‏לא `<id>/<id>/`)   | OPFS walk ‏אחרי כתיבה                                                               |
| 4   | ‏עדיין 0 /api/fs ‏ל-local                              | Network tab                                                                         |
| 5   | ‏רגרסיה: server vault ‏עובד (‏HttpFilesystem ‏לא נגעו) | ‏פתח server vault, ‏ערוך, ‏נשמר לדיסק                                               |
| 6   | self-test ‏של OpfsStore עדיין ALL PASS (23)            | ‏פתח opfs-store.selftest.html                                                       |
| 7   | 21 mobile unit-tests ‏ירוקים                           | `node --test src/client-mobile/test/`                                               |
| 8   | ‏שינוי רק ל-capacitor-shim.js (+walkthrough)           | `git diff --name-only opfs-geturi-fix..HEAD`                                        |

---

## §6 — Risks + mitigations

| ‏סיכון                                 | ‏מיטיגציה                                                                                                                                                        |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ‏נרמול כפול (trash)                    | §3: trash ‏מחוץ ל-OPFS_PATH_METHODS; ‏passthrough → deleteFile ‏המנורמל                                                                                          |
| ‏פספוס מתודה ברשימה → path ‏לא מנורמל  | §3 ‏מונה את כולן; DoD#1 (workspace) + DoD#3 (‏מיקום קבצים) ‏catch-all                                                                                            |
| `Object.create` ‏שובר bind ‏ב-Proxy    | ‏ה-Proxy ‏עושה `v.bind(b)` ‏על b=wrapped; ‏methods ‏של wrapped ‏הם closures (‏arrow) → ‏bind ‏לא מזיק; passthrough ‏methods ‏על prototype → `this`=wrapped ‏נכון |
| ‏רגרסיה ל-server                       | ‏העטיפה רק ל-local; HttpFilesystem ‏לא נגעו; DoD#5                                                                                                               |
| ‏directory-prefix (CACHE) ‏לא נבדק E2E | fullPath ‏כבר ממפה; parity ‏עם HttpFilesystem; ‏אם Obsidian ‏שולח CACHE ‏זה יעבוד כמו server                                                                     |
| vendor ‏חסר → render ‏לא נבדק          | §0 workaround                                                                                                                                                    |

---

## §7 — Escalation triggers

- ‏אחרי הנרמול ה-workspace ‏עדיין לא עולה → ‏חוסם רביעי; ‏דווח trace ‏של הקריאה שנכשלת.
- ‏נרמול שובר את self-test ‏של OpfsStore (‏לא אמור — ‏לא נוגעים בו).
- ‏רגרסיה ל-server vault.
- vendor ‏חסר וחוסם.

---

## §8 — Complexity + verifier

| ‏פרמטר                                                  | ‏ניקוד |
| ------------------------------------------------------- | ------ |
| ‏שימוש חוזר ב-fullPath ‏קיים, ‏עטיפה מכנית              | -1     |
| ‏root-caused + fix-simulated ‏פעמיים                    | -2     |
| ‏עטיפת Proxy/backend — ‏עדינות (trash/bind/passthrough) | +2     |
| ‏אימות = render ‏מלא של Obsidian על OPFS                | +3     |
| ‏רגרסיה dual-path                                       | +2     |
| ‏קושי unit-test (‏adapter layer) → ‏תלות ב-E2E          | +1     |

**Score**: 5/10. **Tier**: `calev-heavy` — ‏האימות הקריטי: ‏workspace ‏עולה על local OPFS vault + ‏מיקום קבצים נכון + ‏רגרסיה.
‏ודא vendor. ‏אם עולה — ‏צלם file-explorer + ‏עורך (‏זה מה שהמשתמשת רוצה לראות).

---

## §9 — ‏שאלות פתוחות

| #   | ‏שאלה                                          | ‏ברירת מחדל                                                                                                  | ‏חוסם? |
| --- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------ |
| 1   | ‏מיקום הנרמול — dispatcher ‏או OpfsStore?      | **dispatcher** — ‏adapter concern; ‏שומר OpfsStore ‏נקי; ‏reuse fullPath. ‏הוכח ע"י 2 ‏חקירות.               | ❌     |
| 2   | ‏unit-test לנרמול?                             | ‏קשה (adapter IIFE); ‏האימות = calev E2E. ‏תיעוד קטגוריה-1 ב-walkthrough.                                    | ❌     |
| 3   | ‏getUri — ‏להשאיר את התיקון מ-opfs-geturi-fix? | ‏כן — root-handling ‏הוא vault-relative concern ‏לגיטימי ב-OpfsStore; ‏מתלכד עם הנרמול (path='' ‏אחרי strip) | ❌     |

---

## ‏סטיות מהתכנון (‏executor)

- ‏(‏ריק)
