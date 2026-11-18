# Site development

The repository uses the GitHub Pages toolchain for its published schema browser. Install the dependencies once.

```bash
bundle install
```

Generate the public schema pages whenever an attributes file, profile, or example changes:

```bash
ruby scripts/generate-schema-pages.rb
```

Then run the site through Bundler:

```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4173
```

Open `http://127.0.0.1:4173/network-specs/schema/`. The server rebuilds after source changes; refresh the page to see them.

The generator writes one thin lowercase `index.md` per schema pack and `_data/schema_packs.json`. GitHub Pages therefore does not need to execute custom plugins. If a generated pack page is absent, the schema index links to that pack's `README.md` as a fallback.

`DEVELOPMENT.md` and the generator are excluded from the published site.

## Production and branch previews

Pages uses GitHub Actions. Production is always built from `main` at `https://openagrinet.github.io/network-specs/`. Existing schema paths remain unchanged. Branch previews are listed at `https://openagrinet.github.io/network-specs/previews/`, with exact commit IDs in `previews/manifest.json`.

Every remote branch containing a schema profile receives a preview, except main and the deployment-only gh-pages branch. URLs use the branch name, such as `/previews/schema-packs-api-driven/`. A slash in a branch name becomes a path separator, so `fix/a` and `fix-a` remain distinct. Commit IDs stay in the banner and manifest, not the URL. Old hash-suffixed preview entry points redirect to the new branch URL. These are public experimental URLs, not production contracts. Push only publishable examples and specifications.

| Event | Behaviour |
|---|---|
| Push to main | Rebuild production and all previews |
| Push to another same-repository branch | Run Check Pages build; a successful push check triggers a trusted main deployment |
| Open or update a PR | Validate the build only; the PR check never triggers deployment |
| Manual Run workflow on main | Refresh immediately after a branch push |
| Branch removed | Its preview disappears after the next successful combined build |

The workflow builds one complete artifact before deploying. A failed build leaves the previously deployed site intact. No branch deploys over the root independently. The single deployment concurrency group serialises publication. An unsuccessful preview build currently blocks that combined refresh; inspect the branch name in the build log, correct it and rerun. This favours a consistent release over publishing a partial preview inventory.

Branches must contain the push-enabled Check Pages build workflow, usually by merging or cherry-picking the infrastructure update from main. No PR is needed for push previews. A push to a branch with an open PR produces both push and PR checks, but only the successful push check can trigger publication. Fork PRs do not trigger publication. There is no scheduled refresh.

### Preview safety and limitations

Main's workflow pins every branch to an exact commit before building. Each matrix job runs on a separate GitHub-hosted runner with read-only repository access, no persisted checkout credentials, no environment secrets and no Pages or OIDC permissions. It installs that branch's dependencies and builds its own generator, templates, styles and scripts with Jekyll safe mode. Do not add secrets, shared caches or self-hosted runners to these jobs.

A fresh assembly job checks out the pinned main revision and downloads static build artifacts from the same workflow run. It never executes downloaded files. The trusted plan determines every destination: main at the root and each branch under its own preview path. Assembly rejects symlinks, hidden files and nested previews. Only the final deployment job receives Pages and OIDC permissions. No artifacts from the triggering PR or push check are reused.

```mermaid
flowchart LR
  P["Successful branch push check"] --> T["Main pins branch commits"]
  T --> B["Isolated read-only builds"]
  B --> A["Trusted job assembles static files"]
  A --> D["Separate job publishes Pages"]
```

Preview layouts now match the branch, including unmerged CSS and JavaScript. These pages share the production site's origin, so only trusted same-repository contributors may publish previews. This is not suitable for untrusted fork code. Artifact retrieval URLs are rewritten to preview paths; vocabulary identifiers remain canonical. Verify external references before using preview contracts for dev validation.

### Setup and recovery

Keep Settings → Pages → Source set to GitHub Actions. The github-pages environment must admit main. Do not disable main's PR or force-push protection. The old schema-packs-v0.1 publishing workflow must not be permitted to deploy over production once the migration is complete.

The last successful site remains online if a new build fails. To republish a known-good renderer, revert the faulty workflow or builder change through a PR, then run Deploy GitHub Pages on main. Do not use Unpublish site. The research stash is independent of this deployment configuration.

Run the dependency-free checks with `python3 -m unittest discover -s scripts -p 'test_pages*.py'`. With the Ruby bundle installed, run `ruby scripts/generate-schema-pages.rb` and `bundle exec jekyll build --safe --destination /absolute/path/to/a/new-build-directory` to check the current branch. The older `build-pages.py` remains a data-only local diagnostic, not the publication entry point. Publication uses `assemble-pages.py` and the isolated matrix builds in `pages.yml`.
