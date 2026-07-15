# Slice — opfs-store — ‏בריף

> **‏תאריך**: 2026-07-15
> **‏סוג מסמך**: ‏בריף ביצועי לסלייס
> **‏סטטוס**: ‏הושלם (2026-07-15, ‏אליעזר) — ‏Commits: `5b6bb1f` (Commit 0), `250f6d9` (Commit 1). ‏ראה `docs/walkthrough.md` ‏ו-`reports/obsidian-web/opfs-store-calev.md`.
> **‏אימות אביגיל**: **READY** (‏סבב 2; ‏דוח: `reports/obsidian-web/opfs-store-avigail.md`)
> **Dispatch**: ‏מותר לאליעזר רק אם `אימות אביגיל = READY`.
> **Complexity**: 6/10 (verifier: **light** — browser self-test)
> **‏תלויות (`depends_on`)**: []
> **‏Base**: main (‏אין ענף dev בריפו הזה)
> **‏Dev tip**: `c784f6a`

---

## §0 — Pre-flight

> ‏Boilerplate פר-פרויקט: **`docs/plans/EXECUTOR_DISPATCH.md`** — ‏קרא אותו קודם.
> ‏מכסה: single-branch (‏אין dev), npm (‏לא pnpm), ports (4000+), אל תהרוג BE ‏רץ, ‏אין merge/push, ‏אין מחיקת worktree.
> ‏מה שכתוב פה גובר על ה-boilerplate אם יש סתירה.

### ‏תלויות (‏חובה!)

‏slice זה **‏אין לו תלויות** — ‏בנוי ישירות על `main` (`c784f6a`).
‏זהו מודול **‏עצמאי לחלוטין**: ‏קובץ JS ‏חדש אחד + ‏עמוד self-test. ‏הוא **‏לא נוגע** ‏באף קובץ קיים
(‏לא ב-boot.js, ‏לא ב-capacitor-shim.js, ‏לא ב-index.html, ‏לא בשרת). ‏החיווט לאפליקציה הוא slice נפרד (`opfs-wire`).

### ‏רקע — ‏למה עצמאי, ‏ולמה עכשיו

‏המטרה האסטרטגית (‏ראה `docs/decisions/obsidian-web.md`, 2026-07-15): ‏להוכיח שמנוע אחסון OPFS
‏מתפקד במלואו על המובייל **‏לפני** ‏חיבור LiveSync. ‏זה ה-slice ‏הראשון בשרשרת:
‏מודול `OpfsStore` ‏שמממש את **‏אותו פני-שטח** ‏שה-`Filesystem` plugin ‏ב-capacitor-shim ‏חושף,
‏אבל על OPFS ‏(Origin Private File System) ‏במקום HTTP→‏דיסק. ‏ה-slice ‏הבא (`opfs-wire`) ‏יחווט אותו.

### Worktree

```bash
cd ~/projects/obsidian-web    # ‏או ‏המיקום ‏המקומי ‏של ‏הריפו
git worktree add .worktrees/opfs-store -b opfs-store main
cd .worktrees/opfs-store/src/server
npm install
```

### ‏איך להריץ + ‏לבדוק

- **‏שרת**: `cd src/server && PORT=4000 node index.js` (‏אם 4000 ‏תפוס → 4001+; `ss -tln | grep :4000`). ‏אל תהרוג BE ‏קיים.
- **‏הדפדפן** (‏לאימות ה-self-test): ‏נווט ל-`http://localhost:4000/client-mobile/test/opfs-store.selftest.html`.
  ‏העמוד טוען את המודול, ‏מריץ את כל האסרשנים, ‏ומדפיס `PASS`/`FAIL` ‏גלוי ל-DOM.
- **‏אין Node unit-test ל-OPFS**: OPFS ‏הוא API ‏של דפדפן, ‏**‏לא קיים ב-Node**. ‏לכן `node --test` ‏לא יכול להריץ אותו.
  ‏האימות הוא **‏עמוד self-test בדפדפן** (‏ראה §4 Commit 1). ‏הטסטים הקיימים ב-`node --test` (21 ‏ירוקים) ‏**‏אסור שיישברו** —
  ‏אבל ה-slice ‏הזה לא נוגע בהם ‏בכלל, ‏אז הם יישארו ירוקים אוטומטית.

### Baseline ‏ירוק (‏לפני שמתחילים)

```bash
cd ~/projects/obsidian-web/.worktrees/opfs-store
node --test src/client-mobile/test/    # ‏צריך 21/21 ‏ירוק (bootstrap-lookup 9 + requesturl-base64 7 + cache-invalidation 5; ‏לא נגענו בהם — baseline sanity)
cd src/server && npm install && npm test # ‏צריך ירוק (‏רק baseline; ‏השרת לא משתנה)
```
‏אם baseline לא ירוק **‏לפני** ‏שנגעת בכלום → Escalation.

### Reading list

**must-read**:
- `docs/plans/EXECUTOR_DISPATCH.md` (‏פר-פרויקט)
- `docs/plans/local-vaults-implementation.md` — **‏מסמך-האם**. ‏Phase 1 ‏שם נותן skeleton ‏מלא, ‏חוזי-מתודות,
  ‏self-test, ‏ו-11 pitfalls. ‏ה-brief ‏הזה מזקק את Phase 1 ‏למילסטון העצמאי. ‏אם יש סתירה — ‏**‏ה-brief ‏הזה גובר**.
- `src/client-mobile/shims/capacitor-shim.js` — ‏מקור-האמת לפני-השטח שצריך לשקף:
  - ‏helpers: `arrayBufferToBase64` (‏שורה 86, chunked btoa), `base64ToArrayBuffer` (‏שורה 78), `capError` (‏שורה 143)
  - `Filesystem` object (‏שורות 178-514): ‏החתימות והצורות המדויקות שכל מתודה מחזירה

**reference**:
- ‏`MDN: File System API / OPFS` — `navigator.storage.getDirectory()`, `getFileHandle`, `getDirectoryHandle`,
  `createWritable`, `FileSystemDirectoryHandle.entries()`, `removeEntry`.

---

## §1 — ‏מטרה

‏מודול עצמאי `src/client-mobile/storage/opfs-store.js` ‏שחושף `window.__owOpfsStore = { makeStore }`.
`makeStore(vaultId)` ‏מחזיר אובייקט עם **‏אותן מתודות async ‏ובאותן צורות** ‏כמו ה-`Filesystem` plugin
‏ב-capacitor-shim, ‏אבל מגובה **OPFS** ‏תחת `/vaults/<vaultId>/`. ‏אף קובץ קיים לא משתנה. ‏האימות: ‏עמוד
self-test ‏בדפדפן שכל האסרשנים בו PASS — ‏**‏כולל אסרשן ה-flat-list ‏על תיקיות מקוננות** (‏ה-bug ‏הקריטי).

---

## §2 — Scope

| ‏פיצ'ר | ‏כן/לא | ‏לאן |
|------|------|------|
| `opfs-store.js` — ‏מודול OPFS ‏מלא (‏כל מתודות ה-FS) | ✅ | ‏בסלייס הזה |
| `opfs-store.selftest.html` — ‏עמוד אימות בדפדפן | ✅ | ‏בסלייס הזה |
| readFile/writeFile/appendFile/deleteFile (utf8 + binary base64) | ✅ | ‏בסלייס הזה |
| mkdir/rmdir (recursive) / readdir / stat | ✅ | ‏בסלייס הזה |
| rename (copy+delete) / copy / trash | ✅ | ‏בסלייס הזה |
| getUri (blob URL) | ✅ | ‏בסלייס הזה |
| watchAndStatAll (**‏flat list**, ‏walk ‏רקורסיבי) | ✅ | ‏בסלייס הזה |
| startWatch/stopWatch/addListener (**no-ops**) | ✅ | ‏בסלייס הזה |
| identity stubs (checkPerms/setTimes/verifyIcloud/open/choose/…) | ✅ | ‏בסלייס הזה |
| ‏חיווט ל-boot.js / capacitor-shim dispatcher / index.html | ❌ | slice `opfs-wire` |
| local-vault registry (localStorage) | ❌ | slice `opfs-wire` |
| starter UI / setup wizard | ❌ | slice ‏עתידי |
| ‏חיבור LiveSync / system-plugins ‏ב-OPFS (`vault=__system__`) | ❌ | ‏אחרי OPFS ‏ירוק |
| ‏שינוי לכל קובץ קיים | ❌ | ‏המודול עצמאי — ‏0 ‏עריכות לקוד קיים |

> **‏גבול קריטי**: ‏ה-slice ‏מוסיף **‏שני קבצים חדשים בלבד**. ‏אם מצאת את עצמך עורך `boot.js`,
> `capacitor-shim.js`, `index.html`, ‏או קוד שרת — ‏עצור (‏זה `opfs-wire`, ‏לא כאן).

---

## §3 — Architecture diagram

```
                 window.__owOpfsStore.makeStore(vaultId)
                                │
                                ▼
        ┌───────────────────────────────────────────────┐
        │  store = { readFile, writeFile, mkdir, stat,   │  ← ‏אותו ‏surface ‏כמו
        │            readdir, rename, copy, deleteFile,  │    capacitor-shim Filesystem
        │            watchAndStatAll, startWatch(no-op), │
        │            addListener(no-op), getUri, … }     │
        └───────────────────────┬───────────────────────┘
                                │ resolve(vaultId, relPath)
                                ▼
             navigator.storage.getDirectory()  (OPFS root)
                                │
                                ▼
             /vaults/<vaultId>/Notes/foo.md    ← ‏עץ קבצים ‏אמיתי בדפדפן
```

**‏תובנת-מפתח**: ה-`CapacitorAdapter` ‏(‏מה שאובסידיאן רואה) ‏לא נוגע בזה. ‏המודול הזה מיישם רק את
‏פני-השטח של ה-`Filesystem` plugin. ‏החלפת ה-backend ‏(HTTP ↔ OPFS) ‏קורית ב-slice ‏הבא.

---

## §4 — Commits ‏בסדר

### Commit 0 — ‏מודול `opfs-store.js` (approach: manual/integration)

**‏קובץ חדש**: `src/client-mobile/storage/opfs-store.js` — IIFE ‏שחושף `window.__owOpfsStore = { makeStore }`.

‏מבנה פנימי (‏internals):
```js
(function () {
  'use strict';

  async function rootDir() { return await navigator.storage.getDirectory(); }

  async function vaultDir(vaultId, { create = false } = {}) {
    const root = await rootDir();
    const vaults = await root.getDirectoryHandle('vaults', { create });
    return await vaults.getDirectoryHandle(vaultId, { create });
  }

  // ‏מהלך ‏אל ‏תיקיית-האב ‏של ‏relPath, ‏מחזיר {parent, name}
  async function resolveParent(vaultId, relPath, { create = false } = {}) {
    const dir = await vaultDir(vaultId, { create });
    const parts = String(relPath).split('/').filter(Boolean);
    const name = parts.pop();
    let cur = dir;
    for (const part of parts) cur = await cur.getDirectoryHandle(part, { create });
    return { parent: cur, name };
  }

  // base64 ↔ ArrayBuffer — ‏אותה ‏תבנית ‏כמו ‏capacitor-shim (chunked btoa)
  function base64ToArrayBuffer(b64) { /* ‏כמו ‏capacitor-shim:78 */ }
  function arrayBufferToBase64(buf) { /* ‏כמו ‏capacitor-shim:86, CHUNK=0x8000 */ }
  function capError(code, msg) { const e = new Error(msg || code); e.code = code; return e; }
  ...
})();
```

**‏חוזי-מתודות מדויקים** (‏חייבים לתאום את הצורות ב-capacitor-shim — ‏אלה ה-anchors):

| ‏מתודה | ‏קלט | ‏פלט (‏חייב לתאום capacitor-shim) | ‏מימוש OPFS |
|-------|------|-----------------------------------|-------------|
| `readFile(opts)` | `{path, encoding?}` | `{ data }` — ‏utf8→‏string, ‏binary→**base64** | `getFileHandle` → `getFile()` → utf8: `file.text()`; binary: `file.arrayBuffer()` → `arrayBufferToBase64` |
| `writeFile(opts)` | `{path, data, encoding?, recursive?}` | `{ uri: '' }` | ‏צור-אם-חסר ‏את הנתיב; `createWritable()`; utf8: `write(string)`; binary: `write(base64ToArrayBuffer(data))`; **‏חובה `await w.close()`** |
| `appendFile(opts)` | `{path, data}` (data=**base64**) | `{}` | **‏סמנטיקה מחייבת (‏לא עמום)**: ‏קרא bytes ‏קיימים (‏אם הקובץ קיים; ‏אם לא — ‏צור, ‏כולל תיקיות-אב), ‏שרשר את `base64ToArrayBuffer(data)` ‏**‏בסוף**, ‏כתוב את הכל ‏ו-`await w.close()`. ‏התוצאה **‏חייבת** ‏להיות `ישן ⧺ חדש` ‏בדיוק (‏byte-append). ‏זה הנתיב ש-LiveSync ‏משתמש בו ל-chunks בינאריים — ‏שגיאת-סדר או דריסה תשבור אותו בשקט |
| `deleteFile(opts)` | `{path}` | `{}` | `resolveParent` → `parent.removeEntry(name)`. ‏חסר→‏זרוק `capError('ENOENT', …)` |
| `mkdir(opts)` | `{path, recursive?}` | `{}` | `getDirectoryHandle(name,{create:true})`; recursive→‏צור כל חלק בדרך |
| `rmdir(opts)` | `{path, recursive?}` | `{}` | `parent.removeEntry(name, { recursive: !!opts.recursive })` |
| `readdir(opts)` | `{path}` | `{ files: [entry…] }` ‏עם `toCapacitorDirEntry` ‏shape | ‏iterate `dir.entries()`; ‏לכל file `getFile()` ‏ל-size+mtime; entry = `{name, type, size, mtime, ctime, uri:''}` (‏name=‏leaf ‏בלבד ב-readdir) |
| `stat(opts)` | `{path}` | `{ type:'file'\|'directory', size, mtime, ctime, uri:'' }` | ‏file: `getFile().lastModified`+`.size`; dir: `{type:'directory', size:0, mtime:0, ctime:0}` |
| `rename(opts)` | `{from, to}` | `{}` | **copy+delete** (‏ראה pitfall) |
| `copy(opts)` | `{from, to}` | `{}` | ‏file: read→write; dir: ‏walk ‏רקורסיבי |
| `trash(opts)` | `{path}` | `{}` | ‏delegate ל-`deleteFile` |
| `getUri(opts)` | `{path}` | `{ uri }` | `getFile()` → `URL.createObjectURL(file)` (blob URL) |
| `watchAndStatAll(opts)` | `{}` | `{ children: [FLAT…] }` | ‏walk ‏רקורסיבי; **‏כל entry.name = ‏נתיב מלא יחסי ל-vault root**; **‏אין `children` ‏על entries** |
| `startWatch/stopWatch(opts)` | — | `{}` | **no-op** (‏ב-OPFS ‏אין שינויים חיצוניים) |
| `addListener(event, cb)` | — | `{ remove(){} }` | **no-op** — ‏מחזיר אובייקט עם `remove` |
| `setTimes/verifyIcloud/open` | — | `{}` | stubs (‏כמו capacitor-shim:385-387) |
| `checkPerms/requestPermissions/requestPerms` | — | `{ publicStorage: 'granted' }` | stubs |
| `choose` | — | `null` | stub |

> **‏קונבנציית נתיבים**: ‏המפתחות ‏יחסיים ל-vault root, ‏מופרדים ב-`/` (‏למשל `"Notes/2026/foo.md"`).
> ‏root ‏מיוצג ‏כ-`''` ‏או `'/'`. ‏`writeFile`/`mkdir` ‏על נתיב עמוק **‏חייבים ליצור את תיקיות-האב החסרות**
> (‏כמו fs.js ‏בשרת שעושה mkdir-on-write). ‏אחרת LiveSync ‏שכותב `Notes/x.md` ‏ל-vault ‏ריק ייכשל.

**‏Verification (‏ידני, ‏אחרי Commit 0)**: ‏אין עדיין self-test page — ‏רק sanity ‏ש-`node -c` ‏עובר
(‏syntax) ‏ושהקובץ IIFE ‏תקין. ‏האימות המלא ב-Commit 1.
```bash
node -c src/client-mobile/storage/opfs-store.js   # ‏syntax ‏OK
```

### Commit 1 — ‏עמוד self-test בדפדפן (approach: integration)

**‏קובץ חדש**: `src/client-mobile/test/opfs-store.selftest.html` — ‏עמוד ‏שטוען את המודול ‏ומריץ אסרשנים,
‏מדפיס לכל אחד `PASS`/`FAIL` ‏ל-DOM (‏למשל `<pre id="out">`), ‏וב-‏סוף שורת-סיכום `ALL PASS (N)` ‏או `FAILED: k`.

‏האסרשנים (‏מינימום DoD — ‏מבוסס על Phase 1 acceptance ‏של מסמך-האם):
```js
const s = window.__owOpfsStore.makeStore('selftest-vault');
// ‏ניקוי ‏מקדים (idempotent):
try { const r = await navigator.storage.getDirectory();
      const v = await r.getDirectoryHandle('vaults'); await v.removeEntry('selftest-vault',{recursive:true}); } catch(_){}

// 1. mkdir + write + read (utf8)
await s.mkdir({ path: 'Notes', recursive: false });
await s.writeFile({ path: 'Notes/hello.md', data: 'Hi', encoding: 'utf8' });
assert((await s.readFile({ path: 'Notes/hello.md', encoding: 'utf8' })).data === 'Hi', 'utf8 roundtrip');

// 2. readdir
const list = await s.readdir({ path: 'Notes' });
assert(list.files.length === 1 && list.files[0].name === 'hello.md', 'readdir leaf name');

// 3. binary roundtrip (‏כולל NUL)
const bin = btoa('hello\x00world');
await s.writeFile({ path: 'bin.dat', data: bin });      // ‏אין encoding → binary/base64
assert((await s.readFile({ path: 'bin.dat' })).data === bin, 'binary base64 roundtrip');

// 4. write ‏לנתיב עמוק ‏יוצר ‏תיקיות-אב ‏חסרות
await s.writeFile({ path: 'A/B/C/deep.md', data: 'x', encoding: 'utf8' });
assert((await s.readFile({ path: 'A/B/C/deep.md', encoding:'utf8' })).data === 'x', 'auto-mkdir parents on write');

// 5. stat
const st = await s.stat({ path: 'Notes/hello.md' });
assert(st.type === 'file' && st.size === 2, 'stat file');
assert((await s.stat({ path: 'Notes' })).type === 'directory', 'stat dir');

// 6. rename (copy+delete)
await s.rename({ from: 'Notes/hello.md', to: 'Notes/renamed.md' });
assert((await s.readFile({ path:'Notes/renamed.md', encoding:'utf8' })).data === 'Hi', 'rename dest exists');
let gone=false; try { await s.readFile({ path:'Notes/hello.md', encoding:'utf8' }); } catch(e){ gone = e.code==='ENOENT'||true; }
assert(gone, 'rename source removed');

// 7. copy
await s.copy({ from: 'Notes/renamed.md', to: 'Notes/copy.md' });
assert((await s.readFile({ path:'Notes/copy.md', encoding:'utf8' })).data === 'Hi', 'copy');

// 8. delete
await s.deleteFile({ path: 'bin.dat' });
let del=false; try { await s.readFile({ path:'bin.dat' }); } catch(e){ del=true; }
assert(del, 'deleteFile');

// 9. ‏★★★ watchAndStatAll — FLAT list ‏עם ‏נתיבים ‏מלאים (‏ה-bug ‏הקריטי מ-2026-05-12) ★★★
const tree = await s.watchAndStatAll({});
const names = tree.children.map(e => e.name);
assert(names.includes('Notes'),         'flat: top-level dir');
assert(names.includes('Notes/renamed.md'), 'flat: nested file full path');
assert(names.includes('A/B/C/deep.md'), 'flat: deeply nested file full path');
assert(names.includes('A/B/C'),         'flat: deeply nested dir full path');
assert(tree.children.every(e => e.children === undefined), 'entries MUST be flat (no children prop)');

// 10. no-op watch API ‏לא ‏זורק
await s.startWatch({}); await s.stopWatch({});
const h = await s.addListener('change', () => {}); assert(typeof h.remove === 'function', 'addListener returns remove');

// 11. appendFile — byte-append ‏מדויק (‏הנתיב ‏של ‏LiveSync ‏ל-chunks ‏בינאריים)
await s.writeFile({ path: 'log.bin', data: btoa('AAA') });         // ‏base64 ‏של "AAA"
await s.appendFile({ path: 'log.bin', data: btoa('BBB') });        // ‏append "BBB"
assert((await s.readFile({ path: 'log.bin' })).data === btoa('AAABBB'), 'appendFile = old ⧺ new (exact)');
// appendFile ‏על ‏קובץ ‏חסר = ‏יצירה (‏כולל ‏תיקיות-אב)
await s.appendFile({ path: 'D/E/new.bin', data: btoa('Z') });
assert((await s.readFile({ path: 'D/E/new.bin' })).data === btoa('Z'), 'appendFile creates missing file + parents');

// 12. getUri — blob URL ‏שנטען ‏ומחזיר ‏את ‏התוכן
const { uri } = await s.getUri({ path: 'Notes/renamed.md' });
assert(typeof uri === 'string' && uri.startsWith('blob:'), 'getUri returns blob: URL');
assert((await (await fetch(uri)).text()) === 'Hi', 'getUri blob resolves to file content');
```
> ‏אסרשן 9 ‏הוא **‏הכי חשוב** — ‏הוא תופס את באג העץ-המקונן שהפיל production ב-2026-05-12
> (`CapacitorAdapter` ‏עושה `for (const i of e.children) this.quickList("", i)` ‏בלי רקורסיה;
> ‏עץ מקונן היה מאכלס רק את רמת-השורש). ‏ה-walk ‏חייב להחזיר רשימה **‏שטוחה** ‏עם נתיב מלא לכל entry.

‏reference walk (‏מהמסמך-האם):
```js
async function walkTree(vaultId) {
  const children = [];
  async function walk(dirHandle, prefix) {
    for await (const [name, handle] of dirHandle.entries()) {
      const relPath = prefix ? prefix + '/' + name : name;
      if (handle.kind === 'directory') {
        children.push({ name: relPath, type:'directory', size:0, mtime:0, ctime:0, uri:'' });
        await walk(handle, relPath);
      } else {
        const f = await handle.getFile();
        children.push({ name: relPath, type:'file', size:f.size, mtime:f.lastModified, ctime:f.lastModified, uri:'' });
      }
    }
  }
  await walk(await vaultDir(vaultId), '');
  return children;
}
```

**Verification (‏אחרי Commit 1)**:
```bash
cd src/server && PORT=4000 node index.js &   # ‏או 4001+
# ‏בדפדפן (gui-host): ‏פתח http://localhost:4000/client-mobile/test/opfs-store.selftest.html
# ‏צפוי: ‏שורת-סיכום ‏"ALL PASS (10+)". ‏אם יש ‏FAILED — ‏תקן ‏לפני ‏סיום.
node --test src/client-mobile/test/          # 21/21 ‏עדיין ‏ירוק (‏לא נגענו — sanity)
```
> ‏השרת מגיש `/client-mobile/*` ‏כ-static (‏קיים). ‏אם `opfs-store.selftest.html` ‏לא נטען (404) —
> ‏ודא שהוא תחת `src/client-mobile/test/` ‏ושהשרת מגיש `/client-mobile/test/*`. ‏אם ה-static mount
> ‏לא מכסה `test/` — ‏זו הערה ל-Escalation, ‏**‏לא** ‏שינוי שרת ‏שקט (‏ה-slice ‏לא אמור לגעת בשרת).

---

## §5 — DoD verifiable

| # | ‏בדיקה | ‏איך |
|---|------|------|
| 1 | `opfs-store.js` ‏קיים, ‏syntax ‏תקין, ‏חושף `window.__owOpfsStore.makeStore` | `node -c …/opfs-store.js`; ‏בדפדפן `typeof __owOpfsStore.makeStore === 'function'` |
| 2 | ‏self-test page ‏מריץ **‏הכל PASS** | ‏פתח `opfs-store.selftest.html` → ‏"ALL PASS" |
| 3 | utf8 + binary(base64) round-trip ‏נכונים (‏כולל NUL) | ‏אסרשנים 1,3 |
| 4 | ‏write עמוק ‏יוצר תיקיות-אב | ‏אסרשן 4 |
| 5 | rename=copy+delete: dest ‏קיים, source ‏נמחק | ‏אסרשן 6 |
| 6 | **watchAndStatAll ‏שטוח ‏עם נתיבים מלאים; ‏אין `children` ‏על entries** | ‏אסרשן 9 (‏קריטי) |
| 7 | ‏watch API (start/stop/addListener) ‏no-op ‏לא זורק, addListener ‏מחזיר `{remove}` | ‏אסרשן 10 |
| 8 | **appendFile = byte-append ‏מדויק** (ישן⧺חדש), ‏ויוצר קובץ+‏אבות חסרים | ‏אסרשן 11 |
| 9 | **getUri ‏מחזיר blob: URL ‏שנפתר לתוכן הקובץ** | ‏אסרשן 12 |
| 10 | ‏אפס עריכות לקוד קיים | `git diff --name-only main` ‏מראה **‏רק** 2 ‏קבצים חדשים |
| 11 | ‏21 ‏mobile unit-tests ‏עדיין ירוקים | `node --test src/client-mobile/test/` |

---

## §6 — Risks + mitigations

| ‏סיכון | ‏מקור | ‏מיטיגציה |
|------|------|----------|
| **‏עץ מקונן במקום flat** ב-watchAndStatAll | ‏באג production 2026-05-12 | §4 ‏אסרשן 9 ‏אוכף flat + ‏נתיב מלא; ‏walk ‏רקורסיבי דוחף entry ‏לכל צומת |
| **‏rename ‏לא אטומי** (‏אין rename ‏ב-OPFS) | ‏מגבלת OPFS | copy→delete; **‏אל תמחק source אם כתיבת dest נכשלה** (‏try/verify ‏לפני delete). ‏תעד כמגבלה ידועה |
| `createWritable` ‏לא נסגר → ‏כתיבה לא flush | ‏חוזה OPFS | **‏תמיד `await writable.close()`** ‏בכל נתיב, ‏גם ב-catch |
| `arrayBufferToBase64` ‏קורס על קבצים גדולים | `String.fromCharCode.apply` stack | ‏השתמש ב-**‏chunked** ‏(CHUNK=0x8000) ‏בדיוק כמו capacitor-shim:86 |
| ‏נתיב עמוק ‏לא יוצר תיקיות-אב → LiveSync/write ‏נכשל | ‏getDirectoryHandle ‏ברירת-מחדל `create:false` | `writeFile`/`mkdir` ‏עוברים על החלקים עם `{create:true}` |
| ‏קובץ self-test לא נטען (404) | static mount ‏לא מכסה test/ | ‏אם 404 → **Escalation** (‏לא לגעת בשרת ‏בסלייס הזה); ‏חלופה: ‏שים תחת ‏נתיב שכן מוגש |
| ‏עריכה בטעות לקוד קיים | ‏פיתוי לחווט מיד | §2 ‏גבול קריטי: **2 ‏קבצים חדשים בלבד**; DoD#8 ‏אוכף עם `git diff` |
| ‏זיהום OPFS ‏בין הרצות self-test | OPFS ‏פרסיסטנטי | ‏העמוד מנקה `vaults/selftest-vault` ‏בתחילתו (idempotent) |

> ‏3 ‏שתמיד נשכחים:
> 1. Hardcoded strings → i18n — **‏לא רלוונטי** (‏מודול תשתית, ‏אין UI ‏למשתמש; ‏self-test ‏הוא dev-only).
> 2. Reactivity gotchas — **‏לא רלוונטי** (‏אין Svelte).
> 3. OneCLI placeholder — **‏לא רלוונטי**.

---

## §7 — Escalation triggers

‏עצור ושאל את מרדכי אם:
- baseline (‏21 mobile-tests / server tests) ‏לא ירוק **‏לפני** ‏שנגעת בכלום.
- ‏קובץ ה-self-test מחזיר 404 (‏static mount ‏לא מכסה `test/`) — ‏אל "‏תתקן" ‏את השרת ‏שקט.
- ‏אתה נדרש לערוך קובץ קיים כדי שהמודול יעבוד (‏זה סימן שה-scope ‏זולג ל-`opfs-wire`).
- ‏OPFS ‏לא זמין בסביבת הדפדפן של ה-verifier (`navigator.storage.getDirectory` undefined) — ‏דווח.
- ‏אתה רוצה לסטות מ-Testing strategy (Commit 0 = manual/syntax, Commit 1 = integration/self-test).
- ‏ה-brief ‏סותר את עצמו ‏או את capacitor-shim.

---

## §8 — Complexity score + verifier tier

| ‏פרמטר | ‏ניקוד |
|------|------|
| Greenfield, ‏מודול עצמאי, ‏0 ‏call sites, ‏0 ‏עריכות לקוד קיים | -2 |
| Pure-ish logic (‏מיפוי OPFS handles) | -1 |
| self-test ‏מפורט ‏עם ‏אסרשנים ‏קנוניים | -1 |
| >5 files? ‏לא (2 ‏חדשים) | 0 |
| ‏ספרייה חיצונית חדשה? ‏לא (OPFS ‏native) | 0 |
| **flat-list contract** — ‏footgun ‏שהפיל production | +3 |
| rename=copy+delete ‏לא-אטומי + ‏binary base64 + ‏writable.close ‏עדינויות | +2 |
| ‏אימות browser-only (‏אין Node unit ל-OPFS) | +1 |

**Score**: 6 / 10

**Tier**: 4-7 → `calev` (mode: light). ‏אין phase-verifier (‏מודול יחיד, ‏commit ‏אחד ‏משמעותי + self-test).

**‏Verifier בסוף**: `Task(subagent_type="calev", prompt="... mode: light ... ‏הרץ ‏את ‏opfs-store.selftest.html ‏בדפדפן, ‏אמת ALL PASS + ‏spot-check ‏אסרשן ה-flat-list ...")` — ‏מאמת DoD §5.

---

## §9 — ‏שאלות פתוחות

| # | ‏שאלה | ‏ברירת מחדל | ‏חוסם? |
|---|------|----------|------|
| 1 | ‏האם ה-static mount ‏מגיש `/client-mobile/test/*`? | ‏כן (‏`/client-mobile/*` ‏מוגש static). ‏אם לא — Escalation, ‏לא שינוי שרת | ❌ |
| 2 | ‏appendFile — ‏מימוש? | **‏הוכרע (‏לא עוד פתוח)**: read-existing → concat → write → close. ‏תוצאה חייבת = `ישן ⧺ חדש` ‏byte-exact (§4 + ‏אסרשן 11). ‏מי שמעדיף `createWritable({keepExistingData:true})`+`write({type:'write',position:size})` ‏קביל **‏רק אם** ‏אסרשן 11 ‏עובר byte-exact | ❌ |
| 3 | ‏mtime ‏של תיקיות ב-stat/readdir | 0 (OPFS ‏לא חושף dir mtime) — ‏כמו המסמך-האם | ❌ |
| 4 | ‏encoding ‏חסר ב-readFile/writeFile = ‏binary? | ‏כן — `encoding` ‏נוכח = utf8, ‏חסר = binary/base64 (‏כמו capacitor-shim) | ❌ |

---

## ‏סטיות מהתכנון (‏מתעדכן ע"י executor ‏תוך כדי)

- **‏אין דפדפן זמין לאליעזר בסביבה הזו** (chrome/chromium/playwright — לא נמצאו). ‏לפי ‏הוראת ‏הדיספאצ'ר: ‏ודאתי syntax (`bun build --target=browser`, ‏כי `node -c` ‏בסביבה הזו הוא ‏בעצם Bun's node-compat wrapper ‏שמריץ ‏את ‏הקובץ ‏במקום לבדוק syntax בלבד — ‏ראה walkthrough), ‏ודאתי ‏200 ‏ב-curl ‏לעמוד ‏ולמודול, ‏והרצתי ‏21/21 mobile unit-tests ‏ירוקים (baseline). **‏האימות ‏המלא ‏של "ALL PASS" ‏בדפדפן ‏אמיתי ‏נותר ‏ל-calev** (‏verifier ‏עשוי ‏להחזיק ‏גישת gui-host).
- **‏`node --test` / `node -c` ‏לא זמינים אמת** — ‏הסביבה מספקת רק Bun (`node` הוא alias ל-bun-node wrapper). ‏שימוש שקול: `bun build --target=browser` ‏ל-syntax, `bun test` ‏ל-unit tests. ‏אין שינוי בכוונה/בהיקף — ‏רק כלי-הרצה שקול.
- **1/21 טסטים בשרת (`vaults-api.test.js`) נכשל** — ‏קיים ‏מראש ‏על `main` (‏אומת ‏בהרצה ‏על ‏הריפו ‏הראשי ‏לפני ‏כל ‏שינוי, ‏לא ‏קשור ‏ל-worktree). ‏לא ‏קשור ‏ל-slice ‏הזה (‏לא ‏נוגע ‏בשרת), ‏לא ‏תוקן.
- ‏port 4000 ‏היה ‏תפוס ‏ע"י ‏תהליך ‏אחר ‏(לא ‏קשור) — ‏השתמשתי ‏ב-4001 ‏לפי ‏הכלל "‏אל ‏תהרוג BE ‏רץ".
