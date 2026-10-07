# SasView Marketplace: adversarial code review

| | |
|---|---|
| **Reviewed** | commit `abd3c29` (`master`, merge of PR #58), 2026-10-06 |
| **Stack at review** | Django 5.2.17, Python 3.12, MySQL 8.0, gunicorn behind Apache |
| **Scope** | the whole repository: models, views, forms, storage backend, templates, `upload_sasmodels.py`, CI/deploy workflows, deploy examples |
| **Prepared with** | Claude Code (AI-assisted), at the maintainer's request |
| **Changes made** | none to application code. This file is the only addition. |

## How to read this

Each finding carries an evidence tag:

- **[V]**: reproduced locally against the pinned stack. The script is in Appendix A.
- **[I]**: established by reading the code.
- **[U]**: could not be verified from the review environment (no access to the live site,
  production settings, or external CDNs). These are phrased conditionally.

Severity is a judgement of impact times reachability for *this* site: a small community site whose
uploads are Python/C plug-ins that SasView users download and run on their own machines.

## Verdict

The design is coherent and, at this size, maintainable. The recent hygiene work is good: Django 5.2
LTS, parameterised SQL in the storage backend, a migration-drift check in CI, a locked-down deploy
pipeline, and solid permission tests.

Three things I would fix first:

1. **Every state-changing action is a GET link** (H1). That is the wrong HTTP method, it bypasses
   Django's CSRF protection, and it is baked into the tests.
2. **The "Verified" badge is not tied to what was verified** (H2). On a site that distributes
   executable code, an owner can swap the files after a staff member has verified the model, and the
   badge stays.
3. **Front-end dependencies are stale, and MathJax points at a CDN retired in 2017** (H3).

Beyond those there is a handful of real, reproducible bugs (vote inflation, 500s on ordinary
uploads) and some deployment/hardening gaps that cannot be assessed from the repository alone.

## Findings at a glance

| # | Sev | Finding | Evidence |
|---|---|---|---|
| H1 | High | State-changing actions are GET links (CSRF, no server-side confirmation) | I |
| H2 | High | "Verified" survives edits and file swaps made after verification | V |
| H3 | High | MathJax loaded from a retired CDN; other third-party JS stale or without SRI | U / I |
| M1 | Medium | Any registered user can inflate a model's score via an invalid `vote` parameter | V |
| M2 | Medium | Uploads are read fully into memory *before* the size check; no request-body limit | I |
| M3 | Medium | Example-data upload returns 500 on a blank line or on more than ~500-700 points | V |
| M4 | Medium | Production security configuration is not in the repo and not checked by CI | I / U |
| M5 | Medium | Open sign-up, no throttling or moderation, human-mediated password resets | I |
| M6 | Medium | Library import script (weekly cron on prod) is non-atomic, swallows errors, untested | I |
| M7 | Medium | `DatabaseStorage`: Latin-1 files crash view and download, wrong sizes, 64 KiB cap | V / I |
| L | Low | Regex DoS in a validator, error-path 500s, structure, docs, CI gaps | see below |

---

## High

### H1. State-changing actions are GET links [I]

**Where.** The views `vote`, `verify`, `toggle_in_library`, `delete`, `delete_file` and
`delete_comment` (`marketplace/views.py`) mutate state on any HTTP method. They are triggered by
plain `<a href>` links in `model_detail.html`, `model_file_edit.html` and `profile.html`. The
existing tests drive them with `client.get(...)`, so the tests document the problem.

**Why it matters.** Django's CSRF protection does not cover GET. A logged-in staff member or model
owner who is navigated to `/models/<id>/delete/`, `/verify/` or `/library/` from another site
performs the action. There is no server-side confirmation: the "Are you sure?" modal is client-side
JavaScript only.

**Calibration.** Django's default `SameSite=Lax` session cookie is in effect under the example
settings (`SESSION_COOKIE_SAMESITE = Lax` [V]). That blocks the "silent" variant: a cross-site
`<img>` or `fetch` will not carry the session cookie in modern browsers. It does *not* block a
cross-site **top-level navigation** (a link click, redirect or `window.location`), which sends Lax
cookies on GET. So exploitation needs the victim to be navigated, not merely to load a page. Impact
is highest for staff, who can delete any model with all its files, verify or unverify models, and
toggle library status. This assumes production does not override the cookie settings (see M4).

**Fix.** Make every mutation POST-only (`@require_POST`) with `{% csrf_token %}` forms. Logout was
already converted for Django 5, so the pattern exists. Keep the JS confirm as UX only. Update the
tests to POST.

### H2. "Verified" is not bound to what was verified [V]

`SasviewModel.verify()` sets a flag; nothing ever clears it. After a staff member verifies a model,
the owner can change the name and description (`edit`) and add or replace files (`edit_files`,
`delete_file`), and the page still says "Verified by <staff member>".

Reproduced: verify a model, then as the owner edit it and upload a new `.py`. Result: `HTTP 302`
both times and `verified = True` afterwards.

This matters more here than on a typical site. The uploaded files are Python and C plug-in models
that SasView users run on their own machines, so the verified flag is the one trust signal for
executable code, and it survives arbitrary edits.

**Fix options, weakest to strongest:**

- Clear `verified`, `verified_by` and `verfied_date` on any non-staff edit or file change.
- Record a hash (SHA-256 over the sorted file contents plus the description) at verification time
  and show "verified" only while it still matches.
- Add a moderation queue: new uploads stay unlisted until a staff member reviews them. Show the file
  hash and a "this is code that will run on your computer" notice on the download page.

### H3. Third-party front-end code [U / I]

**a) MathJax from a retired CDN.** Six templates (`index`, `search`, `category_view`,
`model_create`, `model_edit`, `model_detail`) load
`https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML`. MathJax retired
`cdn.mathjax.org` on 30 April 2017 and promised a redirect to cdnjs for only 3-6 months
([announcement](https://mathjax.org/cdn-shutting-down); see also
[Numbas](https://www.numbas.org.uk/blog/2017/04/important-how-the-shutdown-of-cdn-mathjax-org-affects-numbas/)).

**[U]** The review sandbox could not reach that host, so whether it still redirects, to which
version, or fails outright was not confirmed (check commands are in Appendix B). Either outcome is
bad:

- If it is dead, the LaTeX support advertised on the create and edit forms does not render.
- If it still redirects, the site loads an unpinned third-party script it does not control, with no
  SRI, possibly an old 2.7.x. MathJax before 2.7.4 has an XSS via `\unicode{}` in processed content
  ([CVE-2018-1999024](https://osv.dev/vulnerability/CVE-2018-1999024)), and model descriptions are
  user-authored text that MathJax processes.

The edit and create templates also use the v2-only `MathJax.Hub.Queue` API, so moving to MathJax 3
touches them. Whatever version is chosen, review which TeX macros the configuration enables
(`\href`, `\style`, `\class`, `\cssId`): they allow link injection or CSS overlays in user-authored
descriptions.

**b) Chart.js 2.5.0 (2017)** is loaded from cdnjs with no `integrity` attribute
(`model_detail.html:29`). A CDN compromise would run arbitrary JS on model pages.

**c) Vendored jQuery 2.2.4 (2016) and highlight.js 9.6.0 (2016)** [I; versions read from the
files]. jQuery before 3.5.0 is affected by CVE-2020-11022 and CVE-2020-11023. Neither library is
obviously reachable through the site's own inputs, but both are unmanaged supply chain.

**Fix.** Vendor everything (as is already done for jQuery and highlight.js) or add SRI hashes. Pin
and update versions. Enable Dependabot for `pip` and `github-actions`, and add `pip-audit` to CI.

---

## Medium

### M1. Any registered user can inflate a model's score [V]

In `vote` (`views.py:152-178`), for a user who has already voted, the view first negates the stored
vote and saves it. The `post_save` signal adds that value to `score` immediately. *Then* it reads
`request.GET['vote']`. If the parameter is invalid (HTTP 500) or missing
(`MultiValueDictKeyError`), the first half has been committed and the second never happens. The next
valid vote then double counts.

Reproduced with one user and one `Vote` row: repeating `?vote=bogus` then `?vote=up` moved the score
**1 -> 2 -> 3 -> 4**. Score orders models within a category (`order_by("-score")`), and there is no
rate limit.

**Root cause.** A denormalised counter maintained by signals on every `save()`, a two-step
"undo then redo", and no input validation before mutation.

**Fix.** Validate the input first. Make the change a single atomic step. Add a
`UniqueConstraint(user, model)` on `Vote`. Compute the score from an aggregate, or update it with
`F()` inside a transaction. The signals are registered without a `sender`, so they run for every
model in the project; scope them.

### M2. Uploads are fully read before the size check; no body limit [I]

`ModelFileField.clean` (`forms.py:22-42`) calls `data.file.read()` and runs libmagic over the whole
buffer *before* it checks `max_size`. Django streams uploads to a temporary file but does not cap
their size (`DATA_UPLOAD_MAX_MEMORY_SIZE` does not apply to files), and the example Apache vhost
sets no `LimitRequestBody`. Any registered user (sign-up is open, see M5) can post a very large file
to `/models/create/` or `/models/<id>/files/` and make one of the three sync gunicorn workers read it
all into memory, or fill the temp directory.

Related details in the same field:

- The fallback `except Exception: content_type = data.content_type_extra` assigns a *dict* of
  content-type parameters. If libmagic ever fails, every upload is rejected with a confusing message.
  That fails closed, which is good, but the evident intent was the client-supplied type. "Fixing" it
  that way would fail open on a client-controlled header.
- The extension check is case-sensitive (`.PY` is rejected).
- Downloads are served as `application/force_download` with no `Content-Disposition`. Django's
  default `nosniff` header makes this acceptable, but set `Content-Disposition: attachment` and a
  standard type explicitly.

**Fix.** Check `data.size` first, read only the first few KiB for libmagic, and set
`LimitRequestBody` in Apache.

### M3. Example-data upload fails with 500s on ordinary files [V]

- **Blank line.** Any blank line in the file (a trailing empty line is enough) raises `IndexError`
  (`forms.py:54-55`: `values[0]` is read before the empty-line guard on the next lines).
- **Too many points.** Roughly 500-700 points or more raise
  `DataError: Data too long for column 'example_data_x'`. The parsed numbers are stored in a
  `CharField(max_length=5000)` while the upload limit is 15 KiB. The model-field validators never
  run for these fields because they are not form fields; the view sets them directly. Reproduced
  with a 13,000-byte, 1000-point file under the example settings' `STRICT_TRANS_TABLES`.
- `nan` and `inf` parse as floats and would be emitted into the inline chart script as bare
  identifiers (a ReferenceError that breaks the page's script) [I].
- The y-column parse error reports the *x* value, and the parsing uses bare `except:`.

**Fix.** Handle empty lines, cap or downsample the number of points and surface a form error, and
store the data as JSON emitted with `json_script`.

Note: production's `sql_mode` was not visible to this review. In non-strict MySQL the over-length
case would silently truncate the data and draw a wrong chart instead of failing.

### M4. Production security configuration is invisible and unchecked [I / U]

Only `settings.py.example` (`DEBUG = True`, a public `SECRET_KEY`) is tracked; the real file is
maintained by hand on the server. CI runs `manage.py check` but not `check --deploy`, so nothing
verifies the settings the deployment depends on:

- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` and `SECURE_HSTS_SECONDS`.
- `SECURE_PROXY_SSL_HEADER`: Apache sets `X-Forwarded-Proto: https`, and Django must be told to
  trust it or `request.is_secure()` is false behind the proxy.
- `CSRF_TRUSTED_ORIGINS`.

There is also no `Content-Security-Policy`. The templates rely on inline scripts, so adopting CSP
means moving them out or using nonces. The example Apache vhost has no HSTS header and no
`LimitRequestBody`.

**Fix.** Commit an environment-driven settings module (secrets from the environment or a secret
file) and run `check --deploy` against it in CI. Verify the live headers (Appendix B).

### M5. Accounts: open sign-up, no throttling, manual password resets [I]

`sign_up` is open with no CAPTCHA or email confirmation. There is no login throttling in the repo,
and no moderation or report mechanism, so spam models and comments appear immediately. The login
page tells users to email help@sasview.org so that "one of the admins will reset it for you".
Human-mediated resets are a social-engineering path to account takeover unless identity is checked,
and staff accounts carry outsized power (H1, H2).

**Suggestions.** Add login throttling, optional email confirmation, Django's built-in email-based
reset flow, and stronger protection (2FA or at least strong passwords) for staff accounts.

### M6. Library import script (`upload_sasmodels.py`) [I]

This runs weekly on production under cron.

- **Not atomic.** The update path deletes all `ModelFile` rows and then re-uploads.
  `upload_model_files` catches and *prints* every exception (`except Exception as e: print(e)`), so
  a failed upload leaves a library model with no files while the script exits 0.
- **Broad `except`.** `SasviewModel.objects.get(name=..., in_library=True)` sits inside
  `except Exception: model = None` (lines 58-61). A duplicate name (`MultipleObjectsReturned`) or a
  transient DB error is treated as "model does not exist", and another copy is created.
- **Missing account.** `parse_model` raises `User.DoesNotExist` partway through the loop if the
  `sasview` account is missing. That account must also be `is_staff` (`verify()` enforces it), so
  it is a staff account in the site database.
- **Name matching.** Models are matched by name plus `in_library=True`. If staff flag a user's
  model "in library" in the UI and sasmodels later ships a model with the same name, the script
  overwrites that user's description and files.
- Files are read with the locale's default encoding (`open(file_path, 'r')`). The regex-based RST
  parsing has no tests.

**Fix.** Wrap each model in `transaction.atomic()`, narrow the exception handling, exit non-zero on
failure, use `encoding='utf-8'`, and add tests with a few fixture model files.

### M7. `DatabaseStorage` (vendored 2009 class) [V / I]

- **Latin-1 files crash the site [V].** `_open` does `row[0].decode()` with no error handling
  (`backends/database.py:41`). Upload accepts a Latin-1 `.py` file (for example one with `Å` in a
  comment, which is plausible for scattering scientists). Then the file's view page raises
  `UnicodeDecodeError` and the download returns **HTTP 500**, with the exception text in the body
  (`views.py:235-236`).
- **Wrong sizes [V].** `_save` stores `binary.__sizeof__()` (Python object overhead), not
  `len(binary)`. For `b"second"`, `len` is 6 and `__sizeof__` is 39. Every stored size is wrong.
- **64 KiB ceiling.** The column is a plain `BLOB` (migration 0005). The current 50 KiB model-file
  limit fits, but raising `max_size` would hit a silent MySQL error cliff. Use `MEDIUMBLOB`.
  (The largest file in the sasmodels 1.1.0 wheel is about 21 KB.)
- **Races and fragility.** `get_available_name` then `_save` is a non-atomic check-then-act, and
  the `INSERT INTO ... VALUES(%s, %s, %s)` relies on column order.
- **Architecture.** Files in the database inflate backups and force whole-file reads into memory.
  Fine at this scale, but worth revisiting if usage grows.

**Fix.** Return bytes (`BytesIO`) from `_open` and decode with `errors="replace"` for the preview
only. Use `len(binary)`.

On the good side, values are parameterised and the table and column names come from trusted
settings (see `DatabaseStorageTests`).

---

## Low

**Correctness and robustness**

- **Regex DoS in `validate_comma_separated_float_list`** (`validators.py`) [V].
  `^([-+]?\d*\.?\d+[,\s]*)+$` has nested quantifiers over overlapping classes. Time to reject a
  digit run followed by one bad character:

  | input length | 11 | 13 | 15 | 17 | 19 | 21 |
  |---|---|---|---|---|---|---|
  | time | 0.002 s | 0.011 s | 0.074 s | 0.52 s | 3.5 s | 24 s |

  Roughly 7x slower per two extra characters. It is only reachable today through the Django admin
  form for those two fields (the public forms never validate them, see M3), so it is latent. Replace
  it with a split-and-`float()` validator.
- `delete_file` and `delete_comment` use `.filter().first()` and then attribute access, so a missing
  id gives a 500 (`views.py:245-246`, `279-280`). Use `get_object_or_404`.
- `vote` without `?vote=` raises `MultiValueDictKeyError` (see M1).
- `profile` is not `@login_required`: anonymous `/accounts/profile/` returns 404 instead of
  redirecting to login.
- `search`: a bare `except: pass` around the `verified` parameter, and the pagination links drop the
  `verified` filter (`search.html:96,100`).
- `show_file` has a bare `except:` that wraps only the render.
- Deleting a user cascades to all their models, files, comments and votes. That includes the
  `sasview` library account, whose deletion would wipe every library model. Prefer `PROTECT` or
  deactivation.
- There is no way to remove example data once uploaded: the edit view only overwrites when a file is
  provided.
- Category slugs `create` or all digits are shadowed by earlier URL patterns. The
  `accounts/password_change` patterns are unanchored (no `$`).
- N+1 queries on list pages: `model.owner` and `model.category` are not `select_related`, and
  `comment.user` is queried per comment.

**Templates and front-end**

- Inline JS interpolation (`{{ model.name }}` inside JS string literals: `model_detail.html:63,184`,
  `profile.html:105`) is **not an XSS**. I tested it: Django's autoescape neutralises `<`, `>` and
  both quote characters, so a `</script>` breakout is not possible [V]. A name ending in a
  backslash is not escaped and breaks the inline script on that page, which is self-inflicted.
  Use `escapejs` or `json_script`.
- `example_data_json()` (`models.py:67-76`) builds pseudo-JSON by string concatenation, with
  unquoted keys and a trailing comma. Use `json.dumps` and `json_script`.
- `model_detail.html:53` tests `model.example_data_x and model.example_data_x` (should be `_x and _y`).
- Duplicate `id="model-desc"` per table row; a stray `</tbody>` inside the loop in `search.html:81`;
  `<h3 id="model-name"></h1>` mismatch in the create and edit templates.

**Structure**

- `pre_delete` and `post_save` receivers in `models.py` have no `sender`, so they run for every
  model in the project. `receivers.py` is imported from `urls.py` for its side effects; move that to
  `AppConfig.ready()`.
- `helpers.check_owned_by` is never called.
- The field name `verfied_date` is baked into migrations; fix it with a rename migration.
- `wsgi.py` has a bare `except`, `print` debugging, a "Pyton" typo, and sends itself `SIGINT` on
  startup failure.
- Pinned `requirements.txt` has no hashes or lock for transitive dependencies.

**Tests**

- 33 tests pass in about 31 s [V], mostly password hashing; use a fast hasher in test settings.
- Permission coverage is good. Gaps: no tests for uploads through the views, escaping, the error
  paths above, or `upload_sasmodels.py`. Several tests assert the GET behaviour from H1.

**Process, docs and CI**

- README says Python 3.8 is "what production runs"; the CI and deploy files say 3.12 (Ubuntu
  24.04), and `index.html` still says 3.8. `settings.py.example` still says "Django 1.10".
- README requires at least one approving review on both branches. The API shows **no review at
  all** on PR #55 (the Django 4.2 -> 5.2 upgrade, which went to production) and only an automated
  Copilot comment on PR #57. Either the rule is not enforced for the maintainer (admin bypass) or
  reviews happen elsewhere. Worth confirming the branch-protection settings ("do not allow
  bypassing"), since a merge to `master` auto-deploys to production. Recent history is effectively
  a single human author.
- CI has no linter, no `pip-audit`, and no `check --deploy`. Actions are pinned by tag, not SHA.

---

## What is good

- Django 5.2 LTS on current security releases.
- Parameterised SQL in the storage backend.
- No `|safe`, `mark_safe` or `autoescape off` anywhere in the repo [V: grep], and autoescape holds
  in script context [V].
- CSRF tokens on every POST form; logout moved to POST; login `next` is handled by Django's
  open-redirect checks.
- Permission checks go through one central helper, are enforced server-side for staff-only actions,
  and are decently tested.
- Deploy pipeline design: forced-command SSH key, pinned host key, per-branch GitHub environments,
  tests gating deploys, minimal job permissions.
- A migration-drift check in CI, a clear README with a branch policy, and the automated back-merge
  PR.

## Limitations

- The sandbox could not reach the production site, `cdn.mathjax.org` or `mathjax.org` (the egress
  proxy blocks them). There was no view of the production `settings.py`, the Apache and systemd
  state, database contents, or GitHub branch-protection settings. Findings that depend on those are
  tagged [U] or phrased conditionally.
- The reproductions ran under the example settings (`STRICT_TRANS_TABLES`, `SameSite=Lax`).
  Production may differ.
- This is a point-in-time read of one commit plus a handful of reproductions. It is not a
  penetration test and involved no fuzzing.

## Suggested order of work

Per the README, structural changes go to `dev` first and small self-contained fixes to `master`.

1. **H1 + M1**: POST-only mutations and the vote fix, in one PR with the tests updated (`dev`).
2. **H2**: invalidate or hash verification (`dev`).
3. **H3**: self-host a pinned MathJax 3 and add SRI to the rest. This is the most user-visible fix.
4. **M3 + M2 + M7**: upload and storage robustness. M3 and the Latin-1 case are small `master`
   candidates.
5. **M4**: settings in the repo and `check --deploy` in CI.
6. **M5, M6** and the Low items as capacity allows.

---

## Appendix A: reproduction script

Drop this file next to (not inside) the repo, copy `sasmarket/settings.py.example` to
`sasmarket/settings.py`, make sure the MySQL test user from the README exists, then run it from the
repo root:

```
PYTHONPATH=/path/to/dir/containing/verify_findings python manage.py test verify_findings
```

The tests only print what they observe; nothing asserts, so "bug present" does not fail the run.
The ReDoS timings were taken separately by timing `re.match` on the validator's pattern with
`"1" * n + "x"`.

```python
"""Reproduction script for the findings in docs/code-review-2026-10.md.

Run from the repo root (needs sasmarket/settings.py and a MySQL test database):

    PYTHONPATH=<dir containing this file> python manage.py test verify_findings

Every test only prints what it observes; nothing here asserts, so a "bug present"
result does not fail the run.
"""
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from marketplace.forms import SasviewModelForm
from marketplace.models import ModelFile, Vote
from marketplace.tests import create_model, create_user


class Findings(TestCase):

    def test_cookie_samesite(self):
        print("\n[H1] SESSION_COOKIE_SAMESITE =", settings.SESSION_COOKIE_SAMESITE,
              "| CSRF_COOKIE_SAMESITE =", settings.CSRF_COOKIE_SAMESITE)

    def test_blank_line_in_example_data(self):
        content = b"<X> <Y> <dY>\n0.1 1 0\n\n0.2 2 0\n"
        form = SasviewModelForm({'name': 'n', 'description': 'd'},
                                {'example_data': SimpleUploadedFile('a.txt', content)})
        try:
            print("\n[M3] example data with a blank line -> is_valid():", form.is_valid())
        except Exception as e:
            print("\n[M3] example data with a blank line -> raised", type(e).__name__, e)

    def test_long_example_data(self):
        create_user(sign_in=True, client=self.client)
        data = "".join("0.%04d 1.0 0\n" % i for i in range(1, 1001)).encode()
        print("\n[M3] example data file size:", len(data), "bytes (limit 15360)")
        try:
            r = self.client.post(reverse('create'), {
                'name': 'big', 'description': 'd',
                'example_data': SimpleUploadedFile('big.txt', data)})
            print("[M3] 1000-point example data -> HTTP", r.status_code)
        except Exception as e:
            print("[M3] 1000-point example data -> raised", type(e).__name__, str(e)[:90])

    def test_vote_drift(self):
        model = create_model(user=create_user())
        create_user(sign_in=True, client=self.client)
        url = reverse('vote', kwargs={'model_id': model.id})

        def score():
            model.refresh_from_db()
            return model.score

        self.client.get(url + '?vote=up')
        print("\n[M1] one upvote -> score", score())
        for cycle in range(1, 4):
            self.client.get(url + '?vote=bogus')      # 500, but the "undo" half already saved
            self.client.get(url + '?vote=up')
            print("[M1] after invalid-then-valid cycle", cycle, "-> score", score(),
                  "| Vote rows:", Vote.objects.filter(model=model).count())
        try:
            self.client.get(url)                      # no ?vote= at all
        except Exception as e:
            print("[M1] GET without ?vote ->", type(e).__name__)

    def test_latin1_model_file(self):
        owner = create_user(sign_in=True, client=self.client)
        model = create_model(user=owner)
        r = self.client.post(reverse('edit_files', kwargs={'model_id': model.id}), {
            'model_file': SimpleUploadedFile('latin1.py', b"# q in \xc5^-1\nx = 1\n")})
        stored = ModelFile.objects.filter(model=model).first()
        print("\n[M7] upload of a Latin-1 .py file: HTTP", r.status_code,
              "| accepted =", stored is not None)
        if stored is None:
            return
        for label, url in (
                ('view page', reverse('show_file', kwargs={'file_id': stored.id})),
                ('download', reverse('download_file', kwargs={'filename': stored.model_file.name}))):
            try:
                print("[M7]", label, "-> HTTP", self.client.get(url).status_code)
            except Exception as e:
                print("[M7]", label, "-> raised", type(e).__name__)

    def test_verified_survives_edit_and_file_swap(self):
        staff = create_user()
        staff.is_staff = True
        staff.save()
        owner = create_user(sign_in=True, client=self.client)
        model = create_model(user=owner, name='Original')
        model.verify(staff)
        r = self.client.post(reverse('edit', kwargs={'model_id': model.id}),
                             {'name': 'Something Else', 'description': 'rewritten after review'})
        model.refresh_from_db()
        print("\n[H2] after owner edit: HTTP", r.status_code, "| name =", model.name,
              "| verified =", model.verified)
        r = self.client.post(reverse('edit_files', kwargs={'model_id': model.id}), {
            'model_file': SimpleUploadedFile('swapped.py', b"import os\nos.system('id')\n")})
        model.refresh_from_db()
        print("[H2] after owner uploads a new file: HTTP", r.status_code,
              "| files =", ModelFile.objects.filter(model=model).count(),
              "| verified =", model.verified)
```

## Appendix B: checks that need the live site or the server

Run these from a machine with normal internet access.

```
# H3a: does the retired MathJax host still answer, and where does it send you?
curl -sSIL 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML' | head -20

# M4 / H1: response headers and cookie flags (Secure, HttpOnly, SameSite) on the live site
curl -sSI https://marketplace.sasview.org/accounts/login/ \
  | grep -iE 'strict-transport|content-security|x-frame|x-content|referrer|set-cookie'

# M4: on the server, with the production settings loaded
python manage.py check --deploy

# M3: the SQL mode production actually runs with (strict vs. silent truncation)
python manage.py shell -c "from django.db import connection as c; cur=c.cursor(); cur.execute('SELECT @@sql_mode'); print(cur.fetchone())"
```

In the browser, open a model page with a LaTeX description and look at the console for a failed
MathJax load.
