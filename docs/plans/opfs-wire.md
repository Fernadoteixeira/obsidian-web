# Slice — opfs-wire — ‏בריף

> **‏תאריך**: 2026-07-15
> **‏סוג מסמך**: ‏בריף ביצועי לסלייס
> **‏סטטוס**: ‏מאומת — ‏מוכן ל-dispatch
> **‏אימות אביגיל**: **READY** (‏סבב 2; ‏דוח: `reports/obsidian-web/opfs-wire-avigail.md`)
> **Dispatch**: ‏מותר לאליעזר רק אם `אימות אביגיל = READY`.
> **Complexity**: 7/10 (verifier: **heavy** — E2E ‏מובייל + ‏רגרסיה ל-server vaults)
> **‏תלויות (`depends_on`)**: [`opfs-store`]
> **‏Base**: branch `opfs-store` (‏**‏לא merged** — ‏שרשור!) — tip `c6a7a22`
> **‏Dev tip**: `c6a7a22`

---

## §0 — Pre-flight

> ‏Boilerplate פר-פרויקט: **`docs/plans/EXECUTOR_DISPATCH.md`** — ‏קרא אותו קודם.
> ‏מכסה: single-branch, npm, ports (4000+), אל תהרוג BE ‏רץ, ‏אין merge/push/מחיקת worktree.
> ‏מה שכתוב פה גובר על ה-boilerplate אם יש סתירה.

### ‏תלויות (‏חובה!)

‏slice זה **‏תלוי ב-`opfs-store`** (`depends_on: [opfs-store]`), ‏שעדיין **‏לא נמזג ל-main**.
‏לכן ה-base ‏הוא **branch `opfs-store`** (‏שרשור), ‏לא main:
```bash
cd ~/projects/obsidian-web
git worktree add .worktrees/opfs-wire -b opfs-wire opfs-store   # ← ‏מ-opfs-store, ‏לא main!
cd .worktrees/opfs-wire/src/server && npm install
```
> ⚠️ ‏שרשור: ה-base ‏הוא `opfs-store` (tip `c6a7a22`), ‏שמכיל כבר את `opfs-store.js` ‏ואת ה-self-test.
> ‏אם תפתח מ-`main` — ‏המודול לא יהיה שם ‏וה-dispatcher ‏ייכשל.

### ‏מה `opfs-store` ‏כבר נתן (‏קיים ב-base)

- `src/client-mobile/storage/opfs-store.js` — ‏חושף `window.__owOpfsStore.makeStore(vaultId)`.
  ‏מחזיר אובייקט עם **‏כל 23 ‏מתודות** ה-Filesystem ‏(readFile/writeFile/appendFile/deleteFile/mkdir/rmdir/
  readdir/stat/rename/copy/trash/getUri/startWatch/stopWatch/watchAndStatAll/addListener/setTimes/
  verifyIcloud/open/checkPerms/requestPermissions/requestPerms/choose) — ‏על OPFS ‏תחת `/vaults/<id>/`.
- ‏אומת GO ‏ע"י כלב (self-test ‏בדפדפן, ALL PASS). **‏אל תשנה את המודול** ‏בסלייס הזה.

### ‏רקע — ‏המטרה

‏לחווט את `opfs-store` ‏לאפליקציית המובייל כך ש-**‏vault ‏מקומי (‏מסוג local) ‏רץ 100% ‏בדפדפן על OPFS**,
‏בזמן ש-**‏vaults ‏מסוג server ‏ממשיכים לעבוד בדיוק כמו קודם** (‏אפס רגרסיה). ‏זה הסלייס שבו "‏רואים את OPFS
‏עובד באפליקציה". ‏שרת = ‏מגיש סטטי בלבד לגבי local vaults (‏אין /api/fs, ‏אין /api/bootstrap ‏עבורם).

### Worktree + ‏איך להריץ

- **‏שרת**: `cd src/server && PORT=4000 node index.js` (‏תפוס → 4001+; `ss -tln | grep :4000`). ‏אל תהרוג BE ‏קיים.
- ‏השרת מגיש `/client/*` ‏(‏שורה 90 ‏ב-index.js) ‏ו-`/client-mobile/*` ‏(‏שורה 93) ‏כ-static.
- **‏אימות בדפדפן** (gui-host): OPFS ‏הוא API ‏של דפדפן. ‏האימות המלא הוא בדפדפן אמיתי — ‏לא ב-Node.

### Baseline ‏ירוק (‏לפני שמתחילים)

```bash
cd ~/projects/obsidian-web/.worktrees/opfs-wire
node --test src/client-mobile/test/     # 21/21 ‏ירוק (‏mobile unit — ‏לא נוגעים)
# ‏הערה: ‏טסט שרת ‏אחד (vaults-api.test.js) ‏נכשל ‏pre-existing ‏על main/opfs-store —
# ‏**‏לא ‏שלך ‏לתקן**, ‏לא ‏קשור ‏ל-slice ‏זה. ‏אמת ‏שהוא ‏נכשל ‏גם ‏לפני ‏שנגעת (baseline), ‏והתעלם.
```
‏אם ה-mobile tests ‏לא 21/21 ‏**‏לפני** ‏שנגעת בכלום → Escalation.

### Reading list

**must-read**:
- `docs/plans/EXECUTOR_DISPATCH.md`
- `docs/plans/local-vaults-implementation.md` — ‏מסמך-האם. **Phase 2** ‏(2a registry, 2b boot resolution,
  2c Filesystem dispatcher). ‏ה-brief ‏הזה מזקק את Phase 2 ‏למילסטון המובייל. ‏סתירה → ‏**‏ה-brief ‏גובר**.
- `src/client-mobile/shims/capacitor-shim.js` — `Filesystem` (178-514), `const plugins` (656), PluginHeaders (789).
- `src/client-mobile/boot.js` — VAULT_ID (41), verify block (208-224), bootstrap fetch (236), workspace observer (283).
- `src/client-mobile/index.html` — ‏סדר טעינת scripts (36-59).
- `src/client-mobile/storage/opfs-store.js` — ‏פני-השטח שאליו מחווטים (‏קיים ב-base).

---

## §1 — ‏מטרה

‏אחרי הסלייס: ‏פתיחת `/mobile?vault=<local-id>` ‏על vault ‏רשום ב-registry ‏המקומי → ‏כל פעולות ה-FS
‏עוברות ל-OpfsStore (‏דפדפן), ‏לא ל-HTTP. ‏אפשר ליצור local vault ‏מעמוד מינימלי, ‏לכתוב notes, ‏תיקיות
‏מקוננות, ‏reload ‏שומר. ‏server vaults ‏עובדים כרגיל — ‏0 ‏רגרסיה.

---

## §2 — Scope

| ‏פיצ'ר | ‏כן/לא | ‏לאן |
|------|------|------|
| `src/client/local-vault-registry.js` — registry ‏ב-localStorage (`window.__owLocalVaults`) | ✅ | ‏בסלייס הזה |
| ‏ניתוב vault-type ‏ב-`boot.js` (`__owVaultType` = local\|server) | ✅ | ‏בסלייס הזה |
| ‏branch ‏של בלוק אימות ה-vault + ‏דילוג bootstrap ל-local | ✅ | ‏בסלייס הזה |
| `Filesystem` → Proxy dispatcher (OPFS ↔ HTTP) ‏ב-capacitor-shim | ✅ | ‏בסלייס הזה |
| ‏טעינת registry + opfs-store ‏ב-`index.html` ‏לפני shim+boot | ✅ | ‏בסלייס הזה |
| ‏עמוד יצירה מינימלי `src/client-mobile/new-local.html` | ✅ | ‏בסלייס הזה |
| starter UI ‏מלא (‏מיזוג לרשימת Obsidian) / setup wizard | ❌ | slice `opfs-ux` |
| ‏guard ל-desktop runtime (`/?vault=<local-id>`) | ❌ | slice `opfs-ux` (‏מגבלה ידועה — ‏ראה §6) |
| ‏חיבור LiveSync / system-plugins ‏ב-OPFS | ❌ | ‏אחרי OPFS ‏ירוק |
| ‏שינוי ל-`opfs-store.js` | ❌ | ‏הוא אומת GO — ‏לא נוגעים |
| ‏שינוי בשרת (`src/server/*`) | ❌ | local vaults = static-only; ‏אין endpoint ‏חדש |

> **‏גבול קריטי**: ‏אין שינוי לשרת ‏ואין שינוי ל-`opfs-store.js`. ‏אם נדרש endpoint שרת חדש — Escalation.

---

## §3 — Architecture diagram

```
   index.html ‏טוען ‏בסדר:
   1. /client/local-vault-registry.js   → window.__owLocalVaults
   2. /client-mobile/storage/opfs-store.js → window.__owOpfsStore
   3. /client-mobile/shims/capacitor-shim.js (v=2, ‏עכשיו dispatcher)
   4. ... boot.js  → ‏קובע window.__owVaultType

                    boot.js: VAULT_TYPE = __owLocalVaults.has(VAULT_ID) ? 'local' : 'server'
                                          │
                    ┌─────────────────────┴─────────────────────┐
              'local'                                        'server'
                    │                                            │
   capacitor-shim Filesystem (Proxy)                capacitor-shim Filesystem (Proxy)
                    │ fsBackend()                                │ fsBackend()
                    ▼                                            ▼
         __owOpfsStore.makeStore(id)                    HttpFilesystem (‏הקוד ‏הקיים)
                    ▼                                            ▼
              OPFS ‏בדפדפן                                 /api/fs/* → ‏דיסק ‏בשרת
```

**‏תובנת-מפתח**: ה-Proxy ‏מעריך `__owVaultType` ‏ב-**call-time**, ‏לכן העובדה ש-boot.js ‏רץ **‏אחרי**
‏capacitor-shim ‏לא בעיה — ‏כשאובסידיאן קורא ל-`Filesystem.readFile`, boot.js ‏כבר קבע את הטיפוס.

---

## §4 — Commits ‏בסדר

### Commit 0 — registry ‏מקומי (approach: manual)

**‏קובץ חדש**: `src/client/local-vault-registry.js` — IIFE ‏שחושף `window.__owLocalVaults`.
‏מבוסס על Phase 2a ‏של מסמך-האם. ‏API:
```js
window.__owLocalVaults = {
  list(),                 // [{id, name, createdAt}] ‏ממויין ‏createdAt ‏יורד
  get(id),                // {name, createdAt} | null
  has(id),                // boolean
  create(name),           // {id, name} — id = 16-hex ‏מ-crypto.getRandomValues
  rename(id, name),       // boolean
  remove(id),             // boolean (‏רק ‏מה-registry; ‏מחיקת ‏OPFS ‏באחריות ‏הקורא)
};
```
‏מגובה `localStorage['obsidian-web:local-vaults']` (‏JSON map: `{ [id]: {name, createdAt} }`).

**Verification**: `node -c src/client/local-vault-registry.js` (syntax). ‏אימות פונקציונלי ב-Commit 3.

### Commit 1 — ניתוב vault-type + branch ב-boot.js (approach: integration)

**‏עריכה**: `src/client-mobile/boot.js`.

**(א)** ‏מיד אחרי `VAULT_ID` (‏שורה 41), ‏הוסף:
```js
var VAULT_TYPE = (window.__owLocalVaults && window.__owLocalVaults.has(VAULT_ID)) ? 'local' : 'server';
window.__owVaultType = VAULT_TYPE;
window.__owVaultId   = VAULT_ID;
console.log('[obsidian-web] vault type:', VAULT_TYPE, 'id:', VAULT_ID);
```

**(ב)** ‏בלוק אימות ה-vault (‏שורה ~218, `fetch('/api/fs/stat?vault=…&path=')`) — ‏branch:
```js
var verifyPromise;
if (VAULT_TYPE === 'local') {
  verifyPromise = (async function () {
    if (!window.__owOpfsStore) throw new Error('OPFS store not loaded');
    var root = await navigator.storage.getDirectory();
    var vaults = await root.getDirectoryHandle('vaults', { create: true });
    await vaults.getDirectoryHandle(VAULT_ID, { create: true });   // idempotent
    return { isDirectory: true };
  })();
} else {
  verifyPromise = fetch('/api/fs/stat?vault=' + encodeURIComponent(VAULT_ID) + '&path=')
    .then(function (res) { if (!res.ok) throw new Error('Vault not found (HTTP ' + res.status + ')'); return res.json(); });
}
verifyPromise.then(function (stat) { /* ... ‏המשך ‏הזרימה ‏הקיימת ... */ }).catch(/* ‏קיים */);
```

**(ג) ‏קריטי — ‏דילוג bootstrap ל-local**: ‏בלוק ה-`/api/bootstrap?...&full=1` (‏שורה ~236) ‏שייך **‏רק ל-server**.
‏ל-local vault ‏אין bootstrap בשרת. ‏עטוף אותו ב-`if (VAULT_TYPE === 'server') { ... }`. ‏ל-local:
‏ה-`Filesystem.watchAndStatAll` ‏של OpfsStore ‏מספק את העץ (‏אין צורך ב-bootstrap). ‏ודא שהזרקת ה-scripts
‏של Obsidian (‏i18next/app.js) ‏עדיין קורית בשני הנתיבים — ‏רק ה-bootstrap fetch ‏מדולג ל-local.

> ⚠️ ‏אם תשאיר את ה-bootstrap fetch ‏ל-local → ‏קריאה ל-`/api/bootstrap?vault=<local-id>` ‏תחזיר שגיאה/‏vault
> ‏לא-קיים, ‏והספינר ייתקע. ‏זו נקודת הכשל הכי סבירה — ‏בדוק אותה מפורשות.

### Commit 2 — Filesystem dispatcher ב-capacitor-shim (approach: integration)

**‏עריכה**: `src/client-mobile/shims/capacitor-shim.js`.

1. ‏שנה את שם האובייקט הקיים `const Filesystem = { ... }` (‏178-514) ‏ל-`const HttpFilesystem = { ... }`.
2. ‏**‏הפניות פנימיות**: ‏בתוך המימוש הקיים יש קריאות ל-`Filesystem.deleteFile` (‏שורה 382, trash),
   `Filesystem.startWatch` (‏448, 497). ‏שנה אותן ל-`HttpFilesystem.deleteFile` / `HttpFilesystem.startWatch`
   — ‏אחרת trash/watch ‏של HTTP ‏ינותבו דרך ה-Proxy ‏(‏עלול לפצל בין backends). **‏בדוק את כל 3 ‏המופעים.**
3. ‏הוסף dispatcher ‏אחרי `HttpFilesystem`:
```js
function fsBackend() {
  if (window.__owVaultType === 'local') {
    if (!window.__owLocalFs) window.__owLocalFs = window.__owOpfsStore.makeStore(window.__owVaultId || getVaultId());
    return window.__owLocalFs;
  }
  return HttpFilesystem;
}
const Filesystem = new Proxy({}, {
  get: function (_t, prop) {
    var b = fsBackend();
    var v = b[prop];
    return typeof v === 'function' ? v.bind(b) : v;   // ← bind ‏חובה (‏ראה ‏להלן)
  },
});
```
4. `const plugins = { Filesystem, ... }` (‏שורה 656) ‏נשאר — ‏עכשיו `Filesystem` ‏הוא ה-Proxy.
   PluginHeaders (‏789-802) ‏נשאר — ‏מונה את 23 ‏המתודות; ‏OpfsStore ‏מממש את כולן (‏אומת ב-opfs-store).

> ⚠️ **‏bind ‏חובה — ‏לא אופציונלי** (‏תיקון אביגיל): ‏OpfsStore.`trash` ‏עושה `return this.deleteFile(opts)`
> (`opfs-store.js:331`) — ‏כלומר **‏כן נשען על `this`**. ‏בלי bind, ‏קריאה מפורקת (`const {trash}=Filesystem`)
> ‏תיכשל, ‏וההסתמכות על re-dispatch ‏דרך ה-Proxy ‏שברירית. `v.bind(b)` ‏פותר את זה נקי לשני ה-backends
> (HttpFilesystem ‏אמנם משתמש ב-`HttpFilesystem.deleteFile` ‏מפורשות ‏ולא נשען על this, ‏אבל bind ‏לא מזיק).

### Commit 3 — index.html ‏loading order + ‏עמוד יצירה + walkthrough (approach: integration)

**‏עריכה**: `src/client-mobile/index.html` — ‏הוסף **‏לפני** ‏capacitor-shim.js (‏שורה 36):
```html
<script src="/client/local-vault-registry.js?v=1"></script>
<script src="/client-mobile/storage/opfs-store.js?v=1"></script>
```
> ‏אין צורך לבמפ ידנית את `?v=` ‏של capacitor-shim: ‏השרת כותב-מחדש את כל ה-`?v=` ‏ב-tags ‏של
> `/client(-mobile)/` ‏אוטומטית לפי mtime (`sendHtmlWithCacheBust`, `src/server/index.js:65`, ‏על route `/mobile`).
> ‏פשוט הוסף את שתי השורות בסדר הנכון (‏לפני capacitor-shim ‏שבשורה 36) — ‏ה-busting ‏מטופל.

**‏קובץ חדש**: `src/client-mobile/new-local.html` — ‏עמוד מינימלי (‏עצמאי):
- ‏טוען `/client/local-vault-registry.js`.
- ‏שדה שם + ‏כפתור "Create local vault" → `var {id}=__owLocalVaults.create(name); location.href='/mobile?vault='+id;`
- ‏רשימת local vaults ‏קיימים (`__owLocalVaults.list()`) ‏עם קישור ל-`/mobile?vault=<id>` ‏לכל אחד.
- ‏מינימלי ‏מבחינת עיצוב — ‏זה "‏רואים שזה עובד", ‏לא starter ‏מלא (‏זה `opfs-ux`).

**walkthrough**: ‏entry ‏מתוארך ב-`docs/walkthrough.md`.

**‏Verification (E2E, ‏בדפדפן — ‏אחרי Commit 3)**:
```
1. ‏שרת רץ. ‏פתח /client-mobile/new-local.html → ‏צור "My Notes" → ‏מנווט ל-/mobile?vault=<id>.
2. ‏Console: "vault type: local id: <id>". ‏workspace ‏נטען, vault ‏ריק.
3. ‏צור note + ‏תיקייה מקוננת (Notes/sub/x.md). ‏כתוב תוכן. ‏File explorer ‏מציג את העומק (‏לא תיקייה ריקה!).
4. Reload → ‏הכל נשמר (OPFS ‏פרסיסטנטי). ‏אמת ב-console: OPFS walk ‏מראה את הקבצים.
5. ‏רגרסיה: ‏פתח server vault ‏קיים (‏מה-registry ‏של השרת) → ‏עובד בדיוק כמו קודם, __owVaultType==='server'.
```

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | `__owLocalVaults` API ‏עובד (create/list/has/remove) | console ‏בעמוד היצירה |
| 2 | ‏פתיחת local vault → `__owVaultType==='local'`, ‏workspace ‏נטען | console + UI |
| 3 | ‏כתיבה/קריאה/תיקיות מקוננות ב-local vault → OPFS (‏לא /api/fs) | DevTools Network: ‏אין קריאות /api/fs; OPFS walk ‏מראה קבצים |
| 4 | **File explorer ‏מציג תיקיות מקוננות עם תוכן** (‏flat-list ‏עובד E2E) | ‏צור Notes/sub/x.md → ‏נראה ב-explorer |
| 5 | **Reload ‏שומר הכל** | ‏אחרי reload ‏הקבצים קיימים |
| 6 | ‏bootstrap **‏מדולג** ל-local (‏אין קריאה ל-/api/bootstrap?vault=<local>) | Network tab |
| 7 | **‏רגרסיה: server vault ‏עובד כרגיל** | ‏פתח server vault, ‏ערוך Welcome.md, ‏נשמר לדיסק; __owVaultType==='server' |
| 8 | ‏21 mobile unit-tests ‏עדיין ירוקים | `node --test src/client-mobile/test/` |
| 9 | ‏אין שינוי ל-opfs-store.js ‏ולא לשרת | `git diff --name-only opfs-store..HEAD` — ‏רק ‏הקבצים ב-§2 |

---

## §6 — Risks + mitigations

| ‏סיכון | ‏מקור | ‏מיטיגציה |
|------|------|----------|
| **bootstrap fetch ‏ל-local ‏תוקע ספינר** | ‏בלוק 236 ‏server-only | Commit 1(ג): ‏עטוף ב-`if server`; DoD#6 ‏אוכף |
| **‏פיצול backends** (trash/watch ‏של HTTP ‏דרך Proxy) | ‏הפניות `Filesystem.x` ‏פנימיות | Commit 2.2: ‏שנה ל-`HttpFilesystem.x` ב-3 ‏המופעים (382/448/497) |
| **‏רגרסיה ל-server vaults** | ‏שינוי ה-Filesystem ‏ל-Proxy | DoD#7 ‏בדיקת רגרסיה מפורשת; ‏ברירת-מחדל 'server' ‏שומרת התנהגות קיימת |
| ‏Proxy ‏מאבד `this` (‏למשל OpfsStore.`trash`→`this.deleteFile`) | ‏dispatcher ‏בלי bind | §4 Commit 2.3: ה-Proxy ‏מחזיר `v.bind(b)` ‏לכל פונקציה — ‏חובה (‏trash ‏נשען על this) |
| `__owOpfsStore` ‏לא נטען לפני boot | ‏סדר scripts | Commit 3: ‏register+store ‏**‏לפני** ‏shim ‏ו-boot; boot ‏בודק `if (!__owOpfsStore) throw` |
| ‏OpfsStore ‏חסר מתודה שאובסידיאן קורא | ‏פער surface | ‏אומת ב-opfs-store: ‏כל 23 ‏מתודות PluginHeaders ‏ממומשות |
| ‏שינוי בטעות ל-opfs-store.js/‏שרת | scope creep | §2 ‏גבול; DoD#9 `git diff` |
| ‏desktop `/?vault=<local-id>` ‏התנהגות ‏לא-מוגדרת | ‏אין guard | §6 ‏מגבלה ידועה — ‏guard ב-`opfs-ux`; ‏תעד ב-walkthrough |

> ‏3 ‏שתמיד נשכחים:
> 1. Hardcoded strings → i18n — ‏עמוד new-local ‏מינימלי, ‏dev-facing; ‏מחרוזות באנגלית OK ‏למילסטון.
> 2. Reactivity — ‏אין Svelte.
> 3. OneCLI — ‏לא רלוונטי.

---

## §7 — Escalation triggers

‏עצור ושאל את מרדכי אם:
- baseline (21 mobile-tests) ‏לא ירוק **‏לפני** ‏שנגעת בכלום (‏מלבד ה-server test ‏ה-pre-existing ‏הידוע).
- ‏נדרש endpoint שרת חדש ‏או שינוי ל-`opfs-store.js` ‏כדי לחווט (‏סימן ל-scope ‏לא-נכון).
- ‏פתיחת local vault ‏עדיין פוגעת ב-/api/fs ‏או /api/bootstrap (‏ה-branch ‏לא תפס).
- ‏רגרסיה: server vault ‏נשבר אחרי ה-Proxy.
- ‏Testing strategy ‏סטייה (Commit 0=manual, 1/2/3=integration).
- ‏ה-brief ‏סותר את עצמו ‏או את הקוד.

---

## §8 — Complexity score + verifier tier

| ‏פרמטר | ‏ניקוד |
|------|------|
| ‏נוגע ב-3 ‏קבצים קיימים (boot.js, capacitor-shim.js, index.html) + 2 ‏חדשים | +1 |
| ‏Proxy dispatcher — ‏עדינות (this/bind, ‏הפניות פנימיות) | +2 |
| ‏רגרסיה ל-server vaults ‏חובה לאמת (E2E ‏dual-path) | +2 |
| ‏branch ‏של z-flow ‏ב-boot (bootstrap skip) — ‏נקודת כשל | +2 |
| Greenfield registry (‏פשוט) | -1 |
| ‏תלוי ב-slice ‏מאומת (opfs-store GO) | -1 |
| ‏ספרייה חיצונית חדשה? ‏לא | 0 |

**Score**: 7 / 10

**Tier**: ‏אינטגרציה E2E ‏עם **‏רגרסיה dual-path** ‏+ ‏אימות ויזואלי של file-explorer מקונן →
`calev-heavy` (‏למרות score 7, ‏ה-E2E ‏המובייל + ‏רגרסיה מצדיקים tier ‏גבוה). ‏אין phase-verifier.

**‏Verifier בסוף**: `Task(subagent_type="calev-heavy", prompt="... E2E ‏מובייל: ‏צור local vault, ‏כתוב notes+תיקיות מקוננות, reload, ‏ואמת רגרסיה על server vault ...")` — ‏מאמת DoD §5.

---

## §9 — ‏שאלות פתוחות

| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ‏עמוד היצירה — route ‏ייעודי ‏או static path? | static `/client-mobile/new-local.html` (‏מוגש כבר). route ‏= `opfs-ux` | ❌ |
| 2 | ‏מחיקת OPFS ‏כש-`remove(id)` ‏ב-registry? | ‏לא במילסטון — remove ‏מנקה רק registry; ‏מחיקת OPFS = `opfs-ux` | ❌ |
| 3 | ‏guard ל-desktop `/?vault=<local>` | ‏מגבלה ידועה, ‏מתועדת; guard ‏ב-`opfs-ux` | ❌ |
| 4 | ‏system-plugins (layout) ‏ב-local vault? | ‏למילסטון — local vault ‏רץ בלי system plugins (‏OpfsStore ‏מחזיר ENOENT ל-.obsidian/plugins ‏חסר; Obsidian ‏מדלג). ‏חיווט מלא = ‏אחרי LiveSync | ❌ |

---

## ‏סטיות מהתכנון (‏מתעדכן ע"י executor ‏תוך כדי)

- ‏(‏ריק)
