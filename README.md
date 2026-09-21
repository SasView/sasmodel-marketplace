# SasView Model Marketplace

A website where the small-angle scattering community shares custom plug-in fitting models for
[SasView](https://github.com/SasView/sasview). Models are written as plugins to the
[sasmodels](https://github.com/SasView/sasmodels) infrastructure and uploaded here to share.

[![Tests](https://github.com/SasView/sasmodel-marketplace/actions/workflows/test.yml/badge.svg)](https://github.com/SasView/sasmodel-marketplace/actions/workflows/test.yml)

- Production: https://marketplace.sasview.org
- Staging: https://marketplacedev.sasview.org

Django + MySQL, served by gunicorn behind Apache. Uploaded model files are stored in the
database itself (`marketplace.backends.database.DatabaseStorage`), not on disk.

## Branches and contributing

| Branch | Deployed to | What goes here |
|---|---|---|
| `master` | marketplace.sasview.org | Small, self-contained fixes |
| `dev` | marketplacedev.sasview.org | Structural changes, tested on staging before release |

- Both branches are protected: changes arrive only by pull request, with at least one approving
  review. **Reviewers: check the PR targets the right branch before approving.**
- A structural change is merged to `dev`, tested on the staging site, and released by merging
  `dev` into `master`.
- Every change merged to `master` is merged back into `dev` straight away, so `dev` never falls
  behind production.

## Local development

Requires Python 3.8 (what production runs) and a MySQL server.

1. Create a database and user matching `sasmarket/settings.py.example`, or edit the copy you make
   in step 3:

   ```sql
   CREATE DATABASE marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'mysql'@'localhost' IDENTIFIED BY 'test';
   GRANT ALL PRIVILEGES ON *.* TO 'mysql'@'localhost';
   ```

   (Global privileges let Django create its test database; don't use this user anywhere real.)

2. Install dependencies into a virtual environment. `mysqlclient` needs the MySQL client
   development headers (`libmysqlclient-dev` and `pkg-config` on Ubuntu), and `python-magic` needs
   `libmagic`.

   ```
   python -m venv virtualenv
   source virtualenv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure and run:

   ```
   cp sasmarket/settings.py.example sasmarket/settings.py
   python manage.py migrate
   python manage.py runserver
   ```

4. Before opening a pull request:

   ```
   python manage.py makemigrations --check --dry-run   # no un-committed model changes
   python manage.py test
   ```

   The same checks run on GitHub Actions for every pull request to `master` or `dev`.

`settings.py` is deliberately not tracked. **Never deploy with the example's `SECRET_KEY`** — it
is public. Generate one with
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.

## Production layout

Both sites run on the same host, each from its own checkout and virtual environment:

| | Production | Staging |
|---|---|---|
| Checkout | `/var/www/marketplace.sasview.org` | `/var/www/marketplacedev.sasview.org` |
| Database | `marketplace` | `sasmodeldatabase` |
| systemd unit | `marketplace.service` | `marketplacedev.service` |

- gunicorn listens on a unix socket; Apache serves `/static/` and proxies everything else. See
  `deploy/apache-vhost.conf.example` and `deploy/marketplace.service.example`.
- **Changes take effect only after `systemctl restart`.** The units have no reload action, and with
  `DEBUG = False` Django caches templates too.
- After adding or changing static files, run `python manage.py collectstatic` in the checkout.
- The bundled SasView models are refreshed from a `sasmodels` checkout by
  `scripts/update_sasmodels.sh` and `upload_sasmodels.py`.

Deployment is currently done by hand on the server. An automated deploy — tests pass on GitHub,
then the new code is pulled onto the matching site and the service restarted — is being set up.
