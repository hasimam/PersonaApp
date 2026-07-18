# Result Sharing Plan

## Status

Implementation handoff. This document records the agreed product and technical decisions for sharing completed Quick and Deep journey results.

## Decisions already made

- Do not collect email addresses and do not send email.
- Do not add accounts, sign-in, or result recovery by email.
- A user may save or share their result as a generated image.
- The generated image must contain the complete result summary, not only one highlighted result.
- The image includes PersonaApp branding: logo and a small public domain/"Created with PersonaApp" footer.
- A user may create a private result link and a QR code for that link.
- Private result links expire automatically. Initial expiry: **30 days** after creation.
- There is no manual revoke/extend control in the first version. This deliberately avoids accounts, email, and a separate owner-management link.
- No generated image or PDF is stored on PersonaApp servers.
- Results must never be made available through predictable numeric URLs such as `/results/123`.

## Current behaviour and gap

On completion, the backend already stores a `TestRun`, answers, computed gene scores, model matches, feedback, and selected activation. The React page only keeps the assembled result in memory. A refresh, closed tab, or later visit does not show a completed result again. The current `/journey/resume` endpoint is intentionally only for unfinished runs.

The new private link is the safe way to reopen a completed result. It opens a read-only web report backed by a small, safe result snapshot; it is not an image file.

## User experience

### 1. Completion page

After the user has completed the feedback and activation steps and reaches `Journey Complete`, add a `Keep or share your result` section. This placement ensures the report includes the selected activation. It provides:

- `Download full result image`
- `Share full result image`
- `Create private link`
- `Show QR code` (creates a private link first if none exists)

The feature is available for completed production Quick and Deep journeys. It is not available in draft-preview mode because preview results are not persisted.

### 2. Generated result image

Generate a branded PNG in the browser from a fixed PersonaApp report template. It contains a concise version of every result section presented to the user:

- journey type (Quick or Deep) and completed date;
- top genes, including role/rank and score;
- archetype matches and similarity;
- Quran values and scores;
- Prophetic traits and scores;
- selected activation, if the user selected one;
- PersonaApp logo and compact domain/footer.

Do **not** include answers, feedback ratings, database IDs, link tokens, or other internal data.

The image should use compact rows rather than long descriptions so all result categories fit. Start with a portrait social-friendly layout (1080 x 1920). If a future result type cannot fit without illegible text, generate a taller `full report` PNG rather than silently removing sections.

The selected language determines all image text and its layout must support Arabic/RTL.

### 3. Sharing and download behaviour

- `Download`: create the PNG locally and download it to the device.
- `Share`: create the PNG locally and pass it to the browser/device share sheet with `navigator.share({ files })` when available.
- Fallback: if file sharing is unavailable or the user cancels it, offer/download the PNG. Do not treat cancellation as an error.
- The OS share sheet lets the user choose installed apps such as WhatsApp, Messages, Mail, and social apps. PersonaApp does not integrate separately with those services.

### 4. Private report link and QR code

On `Create private link`, show clear copy before creating it:

> Create a private result link? Anyone with this link can view your selected result summary. It expires in 30 days.

After creation, show:

- `Copy link`
- `Share link`
- `Show QR code`
- the expiry date

The QR code encodes the same private link. It is primarily for moving from desktop to phone, but can also be shared. Do not encode result data directly into the QR code.

### 5. Public shared-report page

Route: `/share#<token>`.

The share token is placed in the URL fragment after `#`. Browsers do not send URL fragments to Vercel, Fly, access logs, or other websites. The React page reads the fragment and sends the token to the report API in a request header. This is intentionally safer than putting the token in a route or query string.

The page is a read-only, responsive version of the completed result. It may look like the normal result screen but must not expose controls that modify the original run. It includes:

- complete result summary in the selected language;
- `Download full result image` and `Share full result image`;
- `Show QR code` / `Copy link` for the same result link;
- `Start your own journey` (not "Restart", because the visitor may not be the original participant);
- a visible expiry/error state after the link expires.

It must not show or change feedback controls, the activation-selection workflow, answers, internal IDs, or other private data.

## Privacy and consent

- Creating a link is explicit: never create one automatically just because a test was completed.
- Downloading/sharing the image is explicit: the user presses the relevant button.
- No email, accounts, cookies for identity, contact lists, or recipient information are collected.
- The image is built locally in the browser and is not uploaded to PersonaApp.
- A link holder can see only the result summary selected above. They cannot edit it, submit feedback for it, select its activation, delete it, or extend its lifetime.
- The sharing UI must say that anyone with the link or QR code can view the report until expiry.
- Add or update the privacy notice to describe the temporary share-link record, small result snapshot, and 30-day retention.

## Security model

There are two capabilities with different purposes:

1. **Owner token**: returned only when a journey starts and retained locally by the original browser. It authorizes every production operation that reads or changes a specific test run: resume, submit answers, submit feedback, select activation, cancel, and create a share link. It is never placed in a URL.
2. **Share token**: a long, cryptographically secure value included only in the fragment of the `/share#<token>` URL. It authorizes read-only viewing until expiry.

The owner token is necessary because numeric `test_run_id` values are guessable. A request using only a test-run ID could otherwise resume, overwrite, cancel, add feedback to, select an activation for, or create a share link for another person’s run.

The app cannot distinguish the original user from another person who has the same share URL. Consequently, the public share URL provides read-only access only. Manual revocation is intentionally out of scope; automatic expiry solves the initial privacy requirement without a second management link, account, or email.

### Token requirements

- Generate owner tokens with `secrets.token_urlsafe(32)` or an equivalent cryptographically secure generator.
- Generate each share token from a random 32-byte seed and HMAC-SHA256 using a purpose-derived key from the existing server `SECRET_KEY`. Store the random seed and SHA-256 token hash, but never the raw token. This lets the server reproduce the same active token for the verified owner without storing it in recoverable form in the database.
- Compare token hashes server-side using constant-time comparison where applicable.
- Never log raw owner or share tokens.
- Do not put owner tokens in query strings, routes, analytics events, exception messages, or image metadata. Do not put share tokens in request paths, query strings, analytics events, exception messages, or image metadata.
- Shared-page and shared-report responses must use `Cache-Control: no-store` and `Referrer-Policy: no-referrer`.
- Return 404 for unknown, expired, or disabled tokens to avoid revealing their state.
- Rate-limit link creation and shared-report reads by IP to reduce abuse. Use conservative limits that do not harm normal users.

## Backend design

### Data model

Add to `test_runs`:

```text
owner_token_hash: string, nullable only for existing historical rows
```

Add a `result_shares` table:

```text
id: integer primary key
test_run_id: foreign key -> test_runs.id, indexed
token_seed: string
token_hash: string, unique, indexed
language: "en" | "ar"
snapshot_jsonb: object
expires_at: timestamp with timezone, indexed
created_at: timestamp with timezone
unique: (test_run_id, language)
```

Rules:

- Keep at most one share row per test run and language. Enforce this with a database uniqueness constraint, not only application logic.
- Creating a link must run in a transaction that handles simultaneous requests safely.
- Return the same token and expiry for an existing unexpired row. Returning it must not extend its expiry.
- If an expired row has not yet been cleaned up, replace its seed, hash, snapshot, and expiry atomically. The old link remains invalid.
- Build `snapshot_jsonb` when the link is created. Store only the public report fields: journey type, completion date, localized result names and scores, ranks/roles, and selected activation content. Do not store answers, feedback ratings, database IDs, owner tokens, or raw share tokens in the snapshot.
- Delete expired share rows, including their snapshots, through scheduled cleanup. Expired rows must never return report content.
- Keep the original `TestRun` data according to the application’s existing retention policy; the separate share row has a 30-day lifetime.

### Journey changes

1. `POST /api/v1/journey/start`
   - Generate an owner token.
   - Store its hash on the new `TestRun`.
   - Return the raw owner token only in `JourneyStartResponse`.
2. Frontend resume storage
   - Store the owner token alongside the current test-run ID while the journey is active.
   - Do not store it after the user clears browser data; no recovery is promised in v1.
3. Protected production journey endpoints
   - Require `X-Result-Owner-Token` on `/resume`, `/submit-answers`, `/feedback`, `/cancel`, and `/shares`.
   - Use one reusable backend verifier for the test-run ID and owner-token hash.
   - Reject missing or incorrect tokens without revealing whether a test-run ID exists.
   - Keep preview endpoints on their existing signed preview-token flow.
4. Through journey completion
   - Keep the owner token in React state through the completion view so the user can create the link.
   - Clearing unfinished-resume storage after answer submission must not clear the in-memory owner token.
5. Deployment transition
   - Historical rows may have a nullable owner-token hash, but they cannot be resumed, changed, or shared through owner-protected APIs.
   - An unfinished journey open during deployment may require a one-time restart. Do not add an insecure compatibility bypass.

### New share API

Use request headers for both capabilities, never request URLs.

```text
POST /api/v1/journey/shares
header: X-Result-Owner-Token: <owner_token>
body: { test_run_id, language }
response: { token, expires_at }

GET /api/v1/shares/report
header: X-Result-Share-Token: <share_token>
response: SharedJourneyResultResponse
```

`POST /journey/shares` must verify all of the following:

- owner-token hash matches the specified test run;
- test run is completed;
- a selected activation has been persisted, so the snapshot represents the final completion page;
- not preview mode;
- requested language is supported.

It must then build the safe localized `SharedJourneyResultResponse`, store that exact response as `snapshot_jsonb`, and create or return the single active row using the transactional rules above.

`GET /shares/report` must:

- hash and find the token;
- reject expired/unknown tokens with 404;
- return the stored snapshot rather than rebuilding it from mutable reference data;
- return only the read-only report fields listed in this document;
- set `Cache-Control: no-store` and `Referrer-Policy: no-referrer`.

Implement snapshot construction as a reusable backend function rather than copying the submit-time response builder. At link creation it must safely build the result from `ComputedGeneScore`, `ComputedModelMatch`, `TestRun.selected_activation_id`, and the relevant reference data. Storing the completed snapshot ensures later edits to reference labels or translations do not change an already-shared report.

### Configuration

Add one server setting, with a documented default:

```text
RESULT_SHARE_TTL_DAYS=30
```

No email-provider key, object storage, image-generation service, or new paid third-party service is required.

## Frontend design

### Components and responsibilities

- `ResultSharingActions`: actions on normal and public report pages; receives read-only report data.
- `ShareLinkDialog`: consent text, create/copy/share link, expiry date.
- `ResultQrCode`: renders the private URL locally.
- `ShareableResultImage`: hidden, fixed-size React template containing the complete compact report.
- `generateResultImage()`: rasterizes that template to PNG locally.
- `SharedResultPage`: serves `/share`, reads the token from `window.location.hash`, removes it from component state when no longer needed, and sends it only through `X-Result-Share-Token`.

The share API returns `{ token, expires_at }`. Construct the public link in the browser as `${window.location.origin}/share#${token}`. The backend does not need to know the frontend’s public domain, so local, staging, production, and future custom domains use the correct origin automatically.

Use a client-side DOM-to-image/canvas approach; a small front-end rasterization/QR dependency is acceptable if it correctly supports Arabic fonts and does not make network calls. Load and await required fonts before image generation. Do not call an AI or external image-generation API.

Set `Referrer-Policy: no-referrer` for the shared page and do not load third-party assets from it. The URL fragment is not sent in HTTP requests, but these controls provide defense in depth.

### Browser compatibility

- Feature-detect `navigator.share`, `navigator.canShare`, and file sharing.
- Feature-detect Clipboard API; fall back to a selectable text field if copying fails.
- Always support PNG download even when native sharing is unavailable.
- QR rendering and image download must work without native share support.
- Use accessible buttons, status messages, and keyboard focus. Provide Arabic and English translations.

## Tests and acceptance criteria

### Backend

- Completed owner can create a share link.
- Missing/wrong owner token cannot resume, submit answers, submit feedback, select an activation, cancel, or create a link.
- A completed result cannot be overwritten by calling `submit-answers` again.
- Started/cancelled/preview run cannot create a link.
- A completed run without a selected activation cannot create a link.
- Repeated link creation returns the same token and does not extend expiry.
- Concurrent link-creation requests produce one row and one active token.
- Share token returns the correct completed report in English and Arabic.
- Unknown and expired tokens return 404 without result data.
- Share response contains no answers, feedback ratings, IDs, or owner token.
- Changing reference data after link creation does not change the stored shared report.
- Share tokens do not appear in API paths, query strings, or normal access logs.
- Shared-report responses include `Cache-Control: no-store` and `Referrer-Policy: no-referrer`.
- Expired share rows and snapshots are deleted by cleanup.
- Expiry is calculated from configured TTL.
- Existing journey API tests still pass after owner-token changes.

### Frontend

- Quick and Deep complete results show the sharing section.
- Preview results do not show it.
- Image template contains every required section, logo/footer, and selected language.
- Arabic image/report use RTL and remain readable.
- Image download works without native share support.
- Native share uses a PNG when file sharing is available; cancellation is harmless.
- QR code resolves to the same private link.
- Public links use `/share#<token>`, and the frontend sends the token to the API only in `X-Result-Share-Token`.
- Public links are constructed from `window.location.origin` and work without backend frontend-origin configuration.
- Shared page is read-only and `Start your own journey` starts a fresh run.
- Expired page shows a friendly unavailable state, not an application error.

### Manual verification

- Test on desktop Chrome/Safari/Firefox and mobile Safari/Chrome.
- Confirm a QR code scanned on a phone opens the same report.
- Confirm private link does not expose predictable IDs or raw answers.
- Confirm Vercel, Fly, and application access logs do not contain raw share tokens.
- Confirm no raw result image is uploaded or retained by the backend.
- Confirm the final PNG looks good in English and Arabic before release.

## Cost impact

The first version should have effectively no new fixed monthly cost:

- PNG and QR generation happen in the browser.
- No image files are stored.
- No email is sent.
- The database stores only small share-token records and compact JSON result snapshots for 30 days.
- The backend serves small JSON reports when a private link is opened.

The main existing-resource impact is additional Neon reads and Fly requests for shared reports. At hobby traffic this should be negligible; monitor current provider dashboards after release.

## Out of scope for v1

- Email-to-self, newsletters, reminders, and email verification.
- User accounts and saved-result libraries.
- Manual revoke/extend controls and separate management links.
- Server-side or AI image generation.
- Server-side image/PDF generation or stored image/PDF files.
- Direct integrations with WhatsApp, Instagram, TikTok, or other social networks.
- Open Graph/social preview image generation for pasted private links.
- Tracking recipients, destinations, or image shares.

## Implementation order

1. Add owner-token security to every production journey mutation and add migrations.
2. Add the unique share-token model, deterministic HMAC token generation, snapshot builder, API, cleanup, and response security headers.
3. Add the `/share#<token>` page with expiry state and a fresh-journey action.
4. Add client-side compact full-report PNG generation and download.
5. Add native image sharing, link dialog, copy fallback, and QR code.
6. Add translations, tests, manual mobile/RTL visual QA, and privacy notice update.
