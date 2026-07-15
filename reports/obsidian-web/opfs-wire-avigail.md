---
project: "obsidian-web"
slice: "opfs-wire"
verifier: "avigail"
date: "2026-07-15"
round: 2
verdict: "READY"
findings:
  - id: 1
    severity: "minor"
    category: "wrong-line-number"
    summary: "PluginHeaders range '789-802' is off-by-one: block is 789-801, line 802 is where the Device entry begins"
    source_brief: "§4 Commit 2.4 line 215"
    source_code: "src/client-mobile/shims/capacitor-shim.js:789"
    cost_estimate: "0min (cosmetic; anchor name:'Filesystem' at 789 is exact)"
---

# Plan Verification (Round 2) — opfs-wire

> **Brief**: docs/plans/opfs-wire.md
> **Base**: branch `opfs-store` @ `c6a7a22` (confirmed tip)
> **Verdict**: ✅ READY
> **סבב 1**: USABLE-AFTER-FIX (3 ממצאים). **סבב 2**: כל 3 התיקונים אומתו נכונים ומספיקים. אין בעיה חדשה.

## אימות שלושת התיקונים מסבב 1

### תיקון #1 — bind ב-Proxy (המהותי) — ✅ נכון ומספיק

- **הבעיה המקורית אומתה שוב**: `OpfsStore.trash` עושה `return this.deleteFile(opts)` ב-`opfs-store.js:331`. `makeStore` מחזיר object-literal (`return {` בשורה 179), ו-`trash` הוא היחיד שנשען על `this`. אז `this` = ה-store.
- **התיקון**: ה-Proxy ב-§4 Commit 2.3 (שורה 210) מחזיר `typeof v === 'function' ? v.bind(b) : v`, כש-`b = fsBackend()`. bind ל-b קושר את `this` ל-store → `this.deleteFile` עובד. ✅
- **פותר גם destructuring**: `const {trash} = Filesystem` מקבל פונקציה כבר-bound; קריאה מנותקת לא מאבדת `this`. ✅
- **לא שובר את HttpFilesystem**: HttpFilesystem משתמש ב-`Filesystem.deleteFile`/`Filesystem.startWatch` **מפורשות** (382/448/497, שהברief משנה ל-`HttpFilesystem.x`), לא נשען על `this`. bind ל-b=HttpFilesystem לא-מזיק. ✅
- **שורת §6 risk** (275) עודכנה נכון: "trash נשען על this → v.bind(b) חובה". עקבי.

### תיקון #2 — הסרת bump ידני של ?v= — ✅ נכון

- אומת: `sendHtmlWithCacheBust` ב-`src/server/index.js:60`, regex ה-rewrite בשורה 65, route `/mobile` בשורה 85-86 קורא לו. הברief מצטט `index.js:65` — מדויק.
- ה-regex תופס `src="/client/..."` ו-`src="/client-mobile/..."` (שני ה-tags החדשים) → cache-bust אוטומטי. ההנחיה החדשה מדויקת. ✅

### תיקון #3 — line drift — ✅ נכון (עם nitpick זעיר)

- `const plugins` = שורה **656** (אומת). ✅
- `const Filesystem = {` = שורה **178** (אומת). ✅
- PluginHeaders `name: 'Filesystem'` = שורה **789** (אומת) — anchor מדויק.
- 🟢 nitpick: הטווח שהברief נותן "789-802" — למעשה `name: 'Device'` מתחיל ב-802, כלומר בלוק Filesystem הוא 789-801. off-by-one קוסמטי בלבד; ה-anchor עצמו מדויק והבלוק "נשאר" (אין עריכה שם). ראה §4 בדיקת anchors — מספרי-שורה מתיישנים, ה-anchor הוא הקובע.

## Spot-check שעבר (אין בעיה)

- ✅ `makeStore` + `window.__owOpfsStore` — `opfs-store.js:120,383`.
- ✅ 3 ההפניות הפנימיות ל-Filesystem: `deleteFile`@382, `startWatch`@448, `startWatch`@497 — **בדיוק 3, כמו שהברief אומר**. אין רביעית שהוחמצה (grep `\bFilesystem\b` → 20/178/382/448/497/657/789 בלבד; 657 = ה-Proxy ב-`plugins`, 789 = PluginHeaders).
- ✅ `getVaultId()` **קיים** ב-shim (`capacitor-shim.js:96`) — ה-fallback `window.__owVaultId || getVaultId()` בשורה 201 של הברief לא יזרוק ReferenceError.
- ✅ אין TDZ: ה-Proxy `const Filesystem` מוכרז אחרי HttpFilesystem (~514) ולפני `const plugins` (656) שמפנה אליו (657).
- ✅ boot.js anchors: `VAULT_ID`@41, `/api/fs/stat`@218, `/api/bootstrap?...&full=1`@237, workspace observer@283 — כולם קיימים.
- ✅ index.html: `capacitor-shim.js` @36 — שתי השורות החדשות נכנסות לפניו כנדרש.
- ✅ File paths: `src/client/` קיים; `src/client/local-vault-registry.js` ו-`src/client-mobile/new-local.html` אינם קיימים (קבצים חדשים אמיתיים).
- ✅ depends_on: `[opfs-store]`, base tip `c6a7a22` = tip אמיתי של branch opfs-store. עקבי.
- ✅ עקביות שמות: `HttpFilesystem`/`Filesystem`(Proxy) בשימוש עקבי לאורך §3/§4/§6.

## הערה על bind (לא ממצא — FYI למרדכי)

ה-Proxy `get` יוצר פונקציה bound **חדשה בכל גישה** (identity לא יציב). בדקתי — אף קוד ב-shim/opfs-store לא משווה identity של מתודות Filesystem (`addListener` מחזיר `{remove(){}}` ריק, לא נשמר לפי identity). לכן לא בעיה. מציין רק לשקיפות.

## Verdict

✅ **READY** — שלושת התיקונים מסבב 1 אומתו נכונים ומספיקים. לא נפתחה בעיה חדשה. הממצא היחיד הוא 🟢 קוסמטי (off-by-one בטווח PluginHeaders) שאינו חוסם ואינו דורש עריכה. מותר dispatch לאליעזר.
