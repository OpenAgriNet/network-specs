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

Every remote branch containing a schema profile receives a preview, except main and the deployment-only gh-pages branch. URLs use a readable branch slug plus a stable eight-character hash, so names such as `fix/a` and `fix-a` cannot collide. These are public experimental URLs, not production contracts. Push only publishable examples and specifications.

| Event | Behaviour |
|---|---|
| Push to main | Rebuild production and all previews |
| Push to a same-repository branch with an open PR | Rebuild through the PR synchronize event |
| Push to a branch without an open PR | Picked up by the 15-minute scheduled refresh; GitHub may delay schedules |
| Manual Run workflow on main | Refresh immediately after a branch push |
| Branch removed | Its preview disappears after the next successful combined build |

The workflow builds one complete artifact before deploying. A failed build leaves the previously deployed site intact. No branch deploys over the root independently. The single deployment concurrency group serialises publication. An unsuccessful preview build currently blocks that combined refresh; inspect the branch name in the build log, correct it and rerun. This favours a consistent release over publishing a partial preview inventory.

For immediate automatic dev URLs, open a draft PR after pushing the branch. Fork PRs do not trigger publication. Their checks can run without deployment privileges, but previews require an explicitly reviewed same-repository branch.

### Preview safety and limitations

The production workflow checks out main and uses main's dependencies, schema generator, layouts and configuration. It imports only ordinary JSON, JSON-LD, YAML, Markdown, HTML and text files from branch schema/, api-schemas/ and api-specs/ directories. It never runs a branch's scripts, Gemfile, custom plugins or workflow. Jekyll runs in safe mode. The build job has read-only repository access; only the separate deployment job receives Pages publication permissions.

This is a schema-content preview, not an arbitrary application deployment. Changes to site templates or generator code need the Check Pages build workflow and local review before merging. Preview artifact URLs are rewritten to their preview paths; vocabulary identifiers remain canonical. Treat preview files as experimental, and verify all external references before using them for dev validation.

### Setup and recovery

Keep Settings → Pages → Source set to GitHub Actions. The github-pages environment must admit main. Do not disable main's PR or force-push protection. The old schema-packs-v0.1 publishing workflow must not be permitted to deploy over production once the migration is complete.

The last successful site remains online if a new build fails. To republish a known-good renderer, revert the faulty workflow or builder change through a PR, then run Deploy GitHub Pages on main. Do not use Unpublish site. The research stash is independent of this deployment configuration.

Run the dependency-free builder checks with `python3 -m unittest discover -s scripts -p 'test_pages*.py'`. With the Ruby bundle installed, validate an unmerged renderer using `python3 scripts/build-pages.py --output /absolute/path/to/a/new-build-directory --test-revision`. Never deploy that test output. Normal publication refuses to run from a revision other than fetched origin/main.
