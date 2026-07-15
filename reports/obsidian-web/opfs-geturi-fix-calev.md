---
slice: opfs-geturi-fix
verifier: calev-heavy
verdict: "PARTIAL"
dod: "8/9 (DoD#5 — workspace על local — נכשל; חוסם שני מוכח)"
findings:
  - id: blocker
    severity: high
    summary: "OpfsStore לא מסיר קידומת vaultId (HttpFilesystem.fullPath כן). Obsidian קורא stat({path:vaultId}) ב-vault-open → OpfsStore מחפש ילד בשם vaultId → ENOENT → onboarding. שורש מוכח + fix-simulated (monkeypatch → workspace מלא עלה). מטופל ב-slice opfs-vault-path."
  - id: woff2
    severity: minor
    summary: "2 קבצי vendor *.woff2 חוזרים 404 (font missing מה-bundle) — env noise, קיים גם ל-server, לא רגרסיה."
---
# calev-heavy — opfs-geturi-fix — verdict: PARTIAL

תיקוני getUri + rethrowAsEnoent **נכונים ונחוצים** (8/9 DoD). אבל DoD#5 (★ workspace על local) נכשל
בגלל חוסם שני שהתגלה ונרcause: OpfsStore לא משכפל את חוזה-הנתיבים של HttpFilesystem (vaultId-strip).
fix-simulation (monkeypatch) הוכיח 100% שהסרת הקידומת פותחת workspace מלא על OPFS, 0 /api/fs,
file-explorer עם Welcome.md + Notes/. → slice opfs-vault-path.

screenshots: /tmp/verify/opfs-geturi-fix/ (selftest ALL PASS 23, server-vault workspace,
local-vault-boot stuck, local-vault-PATCHED-workspace = הוכחת התיקון).
