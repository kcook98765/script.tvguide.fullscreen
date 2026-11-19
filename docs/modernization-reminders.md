# Reminder text handoff (task05)

Refs #14, #7, #1. Source repair only, not native reminder acceptance.

## Scope and boundary

Keep the original AlarmClock mechanism, digest-based names/cancellation,
five-minute and start phases, database rules, GUI add/remove and background
service reconstruction. No PVR or metadata add-on is required. Program **and
service** manifest entries are unchanged. Ordinary AutoPlay's delimiter-bearing
channel-ID restriction is still a separate #14 preservation row; it is not fixed
or broadened here. Recording/AutoPlayWith, custom skins, metadata/artwork,
external players, external search and mappings remain tracked, not settled.

Previously `notification.py` applied `is_builtin_data` to title, both localized
channel messages and icon before scheduling either alarm. Apostrophes, quotes,
commas, parentheses and Windows backslashes therefore silently blocked reminders.
That conservative helper remains unchanged for actual command-grammar users.

Now only a constrained 96-hex event token and fixed `5mins`/`now` phase reach
one fixed bundled `reminder_callback.py` RunScript path. The token is the existing
64-hex title/start digest plus a fresh 32-hex registration nonce. No decoded text,
profile code, raw command, caller-selected callback path or action is executed.

`reminder_data.py` stores UTF-8 JSON under the translated add-on profile's
`reminders/<digest>.json`, atomically replacing the complete file. Reads are
limited to 64 KiB, four text fields to 16000 UTF-8 bytes each; exact schema,
version, token/key agreement, fixed scheduled phases and finite year-1970..9999
timestamp are checked.
There is no text escaping, normalization or delimiter-based rejection. The fixed
callback imports neither the guide nor its DB/providers; it passes the original
title, phase body and icon to `Dialog.notification` as data, with **10000 ms and
sound=True**. AlarmClock's trailing True suppresses its own timer notice, not the
reminder sound. See [Matrix GUIBuiltins][builtin] and [toast defaults][toast];
the four tagged Dialog.notification implementations/API semantics are recorded
in [issue14][inventory]. Missing/invalid/oversized data logs a generic error,
never private text. Actual native rendering/sound is untested.

## Lifecycle details and limits

- Whole-minute delays are retained. Already-past programs are not scheduled;
  the missed five-minute phase is skipped inside the last five minutes (Kodi
  rejects negative AlarmClock intervals); the start reminder is still scheduled.
- Reconstruction reuses the registration nonce and persistent per-phase exclusive
  claim files, so a delivered phase is not rearmed. Service descriptions now use
  the channel **title**, matching GUI addition, rather than its database ID.
- Cancel invalidates JSON before removing claims and cancels both digest alarms.
  Re-add creates a new nonce, so stale callbacks cannot consume a new reminder.
  Removing a recurring rule also cancels its other currently scheduled events;
  clear invalidates all stored events and cancels their alarms, not just DB rows.
- Callbacks check identity again after claiming. Duplicates, unknown/unscheduled
  phases and callbacks earlier than their scheduled minute are ignored (60s
  allowance for AlarmClock floor rounding). **There is no lateness cutoff** for
  pending callbacks. A provisional ten-minute expiry was removed during review
  because it could lose a legitimate delayed reminder. Only fully consumed events
  whose start has passed are pruned during scheduling. Separate completion markers
  are written only after API handoff, so cleanup cannot invalidate an in-flight
  phase just because it was claimed. Pending events remain until delivered,
  cancelled or cleared. No new catch-up dispatch on restart is added.
- Claim-before-display is intentionally at-most-once, not a job/retry system:
  process failure after claiming can lose that display. Cancel cannot retract a
  notification already handed to Kodi. Old unsafe raw-name alarms are not replayed
  or migrated. Normal source reconstruction is covered; native restart/race/UI
  acceptance is pending. Existing title/start name collisions are not redesigned.

## Focused evidence

`tests/check_reminders.py` uses only pure helpers, disposable JSON and captured
calls from reviewed AST-extracted methods (no legacy initialization, Kodi/stub
imports or executed alarms). It checks punctuation/Unicode/Windows paths, inert
command-looking text, original exact data in both phases, timing, typed/bounded
JSON, constrained alarm grammar, normal/recurring remove, clear, duplicate claims,
reconstruction, cancellation and stale re-add. Existing command/source/Python3
checks retain the baseline unsafe-source and delimiter controls.

All four scripts run independently under a PATH-only minimal environment,
Matrix-lane Python `-I -B`. Changed source/tests parse with Python3.8 grammar.
Narrow Matrix-stub mypy checks the two new modules; an intentionally wrong
notification signature must still fail. Full original output/stderr, initial
direct-mypy import-untyped diagnostic, receipt-inventory assertion correction and
source hashes are retained in `.git/modernization-evidence/task05-*`.

No four-lane/full-suite rerun: unchanged bytes reuse task03's six-stage receipts
(syntax/manifest/paths/package passed; types and official checker failed, all
warnings retained). They do **not** qualify changed bytes or native behavior.
Matrix19.5 static tools do not establish native19.4; Piers remains bounded RC2.
No Lab calls, lifecycle/import/deploy/launch/smoke, UI/display, screenshots/logs,
production access, release or distribution publication occurred in task05.

[builtin]: https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/builtins/GUIBuiltins.cpp
[toast]: https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/dialogs/GUIDialogKaiToast.h
[inventory]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/14
