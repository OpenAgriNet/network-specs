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
