---
slice: opfs-wire
verifier: calev-heavy
verdict: "GO"
dod: "9/9 (7 fully in real browser, 2 at data-contract layer — env caveat)"
regressions: none
findings:
  - id: F1
    severity: minor
    scope: out-of-DoD
    category: known-limitation
    summary: "cap.convertFileSrc לא מסתעף על __owVaultType — attachments בינאריים גדולים ב-local vault יפגעו ב-/api/fs (HTTP) במקום OPFS. core note editing לא מושפע. נדחה ל-opfs-ux/attachments."
  - id: F2
    severity: environment
    scope: verification-only
    category: env-limitation
    summary: "vendor/obsidian-mobile חסר בסביבת האימות (/obsidian-mobile/* → 404), לכן render מלא של workspace/file-explorer UI לא נבדק דרך אפליקציית Obsidian האמיתית. כל מה שהסלייס שינה אומת בדפדפן אמיתי על OPFS אמיתי. לא defect של הסלייס."
---

# calev-heavy — opfs-wire — verdict: GO

**mode**: heavy | **DoD**: 9/9 | **regressions**: 0 | **findings**: 2 (1 minor out-of-scope, 1 environment)

## סביבה
דפדפן אמיתי (Chromium 151 via playwright-core) על **OPFS אמיתי** — מעבר לסביבת ה-DOM-shim
של ה-executor. מגבלה קשה: vendor bundle של Obsidian לא-מוותר בסביבה (`/obsidian-mobile/*` → 404),
לכן ה-workspace UI המלא לא נרנדר. עקיפה: pre-seed של `window.Capacitor` → `patchCapacitor()`
חושף את ה-Filesystem Proxy האמיתי → הרצה ישירה על OPFS אמיתי / /api/fs אמיתי.

## DoD (§5)

| # | פריט | סטטוס | ראיה |
|---|------|-------|------|
| 1 | `__owLocalVaults` API | ✅ | 16-hex ids, empty→Untitled, 10 rapid creates unique, sort desc, persist across reload |
| 2 | local → `__owVaultType==='local'`, workspace | ✅ wiring / ⚠️ UI | flags נכונים, console `vault type: local`; UI render חסום ע"י app.js 404 (env) |
| 3 | write/read/nested → OPFS לא /api/fs | ✅ | nested Notes/sub/x.md (כולל עברית), **0 קריאות /api/fs** ב-local |
| 4 | file explorer מקונן (flat-list) | ✅ contract / ⚠️ DOM | watchAndStatAll flat list נכון עם נתיבים מלאים; DOM חסום (env) |
| 5 | Reload שומר הכל | ✅ | OPFS walk זהה לפני/אחרי reload |
| 6 | bootstrap מדולג ל-local | ✅ | 0 קריאות /api/bootstrap (0 /api בכלל) |
| 7 | **רגרסיה: server vault כרגיל** | ✅ | server flow שלם: /api/fs/stat + /api/bootstrap + Proxy→HttpFilesystem→PUT/GET; marker נשמר לדיסק ושוחזר |
| 8 | 21 mobile unit-tests ירוקים | ✅ | 21 pass / 0 fail |
| 9 | אין שינוי ל-opfs-store.js / server | ✅ | git diff נוגע רק ב-registry/boot/shim/index/new-local + docs |

## נקודות heavy שנבדקו
- **flat-list contract** (החשש #1): אומת E2E על OPFS אמיתי, עומק נשמר, אין באג "תיקייה ריקה" בשכבת הנתונים.
- **backend split** (השינוי המסוכן): נקי — local=0 /api/*, server=/api/fs+bootstrap נכונים, אין דליפה.
- **bind/this** (תיקון אביגיל): `const {trash}=Filesystem; trash()` על local → OpfsStore.trash→this.deleteFile → מחק בפועל. עובד בדפדפן אמיתי.
- **internal refs**: 3 ההפניות → HttpFilesystem (389/457/507), אין שארית.
- **loading order + call-time Proxy**: registry+opfs-store לפני shim; boot קובע __owVaultType לפני שאובסידיאן קורא ל-FS.

## המלצות
- **F1** → לתעד ל-opfs-ux (attachment story): convertFileSrc צריך להסתעף ל-OPFS blob ל-local. סינכרוני מול async getUri — לא טריוויאלי, ולכן דחייה מוצדקת.
- **F2** → אימות ויזואלי אחד של file-explorer DOM כש-`vendor/obsidian-mobile/` נוכח (scripts/update-obsidian-mobile.js).

**Bottom line: GO** — אפס רגרסיות ל-server vaults, ה-Proxy/bind/bootstrap-skip אומתו על OPFS אמיתי.
ראיות: /tmp/verify/opfs-wire/*.png + JSON dumps.
