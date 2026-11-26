#!/usr/bin/env ruby
# Generate a static documentation page from checked-in provider fixtures.
# Usage: ruby scripts/generate-provider-walkthrough.rb [repository [output]]

require 'cgi'
require 'json'
require 'pathname'
require 'uri'
require 'yaml'
require 'date'
require_relative 'discovery_example'

ROOT = Pathname.new(ARGV.fetch(0, File.expand_path('..', __dir__))).realpath
PAGE = ROOT.join('api/providers/index.html')
OUTPUT = Pathname.new(ARGV.fetch(1, PAGE.to_s))

def escape(value)
  CGI.escapeHTML(value.to_s)
end

def link(label, href)
  %(<a href="#{escape(href)}">#{escape(label)}</a>)
end

def relative(file)
  file.relative_path_from(PAGE.dirname).to_s
end

def read_json(file)
  JSON.parse(file.read)
end

def sample(label, value)
  "<details><summary>#{escape(label)}</summary><pre><code>#{escape(JSON.pretty_generate(value))}</code></pre></details>"
end

def spec_path(url)
  uri = URI.parse(url)
  # Contracts are served from the branch until v0.2 reaches the site; packs
  # still come from the site, so both prefixes resolve to the same repo path.
  match = %r{\A(?:/network-specs|/OpenAgriNet/network-specs/bv-migration)/(api/(?:adapter|external)/[A-Za-z0-9/._-]+/openapi\.yaml)\z}.match(uri.path)
  unless uri.scheme == 'https' && %w[openagrinet.github.io raw.githubusercontent.com].include?(uri.host) && match &&
         (match[1].split('/') & %w[. ..]).empty?
    raise "Not a repository OpenAPI URL: #{url}"
  end
  file = ROOT.join(match[1]).realpath
  raise 'OpenAPI file resolves outside api/' unless file.to_s.start_with?(ROOT.join('api').to_s + '/')
  file
end

def operation(action)
  uri = URI.parse(action.fetch('operationRef'))
  file = spec_path(uri.to_s)
  pointer = URI::DEFAULT_PARSER.unescape(uri.fragment)
  raise "Not an OpenAPI operation: #{uri}" unless pointer.match?(%r{\A/paths/[^/]+/(get|put|post|delete|options|head|patch|trace)\z})
  _, path, method = pointer.split('/').drop(1).map { |part| part.gsub('~1', '/').gsub('~0', '~') }
  spec = YAML.safe_load(file.read, permitted_classes: [Date, Time], aliases: true)
  path_item = spec.fetch('paths').fetch(path)
  contract = path_item.fetch(method)
  operation_id = contract.fetch('operationId')
  kind = spec.fetch('info')['x-contract-role'] == 'adapter-proposal' ? 'Proposed adapter contract (not a provider endpoint)' : 'Documented upstream operation'
  [action.fetch('action'), "#{method.upcase} #{path}", operation_id, kind, "#{relative(file)}##{uri.fragment}",
   contract_details(path_item, contract, relative(file), uri.fragment)]
end

def schema_type(schema, spec)
  return 'No schema specified' unless schema

  if (ref = schema['$ref'])
    ref.start_with?('#/') ? link(ref.split('/').last, spec + ref) : escape(ref)
  elsif schema.key?('type')
    Array(schema.fetch('type')).map { |type| escape(type) }.join(' or ')
  elsif schema.key?('oneOf') || schema.key?('anyOf')
    Array(schema['oneOf'] || schema['anyOf']).map { |option| schema_type(option, spec) }.join(' or ')
  else
    'Inline schema'
  end
end

def content_details(content, spec)
  content.map do |media, description|
    schema = description['schema']
    examples = []
    examples << sample('Example', description['example']) if description.key?('example')
    if !description.key?('example') && schema && schema.key?('example')
      examples << sample('Schema example', schema['example'])
    end
    description.fetch('examples', {}).each do |name, example|
      if example.key?('value')
        examples << sample("Example: #{name}", example['value'])
      elsif example['$ref']
        examples << "<p>#{schema_type(example, spec)}</p>"
      end
    end
    "<p><code>#{escape(media)}</code> · #{schema_type(schema, spec)}</p>#{examples.join}"
  end.join
end

def contract_details(path_item, contract, spec, pointer)
  body = contract.fetch('requestBody', {})
  body_content = content_details(body.fetch('content', {}), spec)
  body_content = "<p>#{schema_type(body, spec)}</p>" if body.key?('$ref')
  parameters = (path_item.fetch('parameters', []) + contract.fetch('parameters', [])).reverse
             .uniq { |entry| [entry['name'], entry['in'], entry['$ref']] }.reverse
  params = parameters.map do |entry|
    if entry.key?('$ref')
      "<li>#{schema_type(entry, spec)}</li>"
    else
      where = [entry.fetch('in'), entry['required'] ? 'required' : 'optional'].join(', ')
      example = entry.key?('example') ? sample('Parameter example', entry['example']) : ''
      "<li><code>#{escape(entry.fetch('name'))}</code> (#{escape(where)}) · #{schema_type(entry['schema'], spec)}#{example}</li>"
    end
  end
  inputs = [params.empty? ? '' : "<ul>#{params.join}</ul>", body_content].join
  inputs = '<p>No parameters or request body in the spec.</p>' if inputs.empty?
  outputs = contract.fetch('responses').map do |status, response|
    href = "#{spec}##{pointer}/responses/#{status}"
    description = if response.key?('$ref')
                    schema_type(response, spec)
                  else
                    escape(response.fetch('description'))
                  end
    "<li>#{link(status, href)} · #{description}#{content_details(response.fetch('content', {}), spec)}</li>"
  end
  "<details class=\"operation\"><summary>Request and responses</summary>" \
    "<p><strong>Request</strong></p>#{inputs}<p><strong>Responses</strong></p><ul>#{outputs.join}</ul></details>"
end

catalogs = ROOT.glob('api/external/*/catalog.json').sort.flat_map do |file|
  read_json(file).fetch('message').fetch('catalogs').map { |catalog| [file, catalog] }
end
offerings = catalogs.flat_map do |file, catalog|
  catalog.fetch('resources').map { |resource| [file, catalog, resource] }
end
codes = offerings.map { |_, _, resource| resource.fetch('descriptor').fetch('code') }
raise 'Duplicate or invalid capability code' if codes.uniq != codes || codes.any? { |code| !code.match?(/\A[a-z0-9-]+\z/) }


direct = %w[
  direct-knowledge-advisory-resource.json direct-market-intelligence-resource.json
  live-mandi-price-resource.json live-weather-advisory-resource.json live-weather-resource.json
].map do |name|
  files = ROOT.glob("schema/*/v*/examples/network/#{name}")
  raise "Expected one network example: #{name}" unless files.one?
  file = files.first
  resource = read_json(file)
  attrs = resource.fetch('resourceAttributes')
  raise "#{file} is not a Direct resource" unless attrs.fetch('informationMode') == 'Direct'

  [file, attrs.fetch('@type'), resource.fetch('descriptor').fetch('name')]
end

providers = catalogs.sort_by { |_, catalog| catalog.fetch('provider').fetch('descriptor').fetch('name').downcase }
mapping_directory = ROOT.join('api/external')
mapping_index = mapping_directory.join('mappings-index.json')
inventory = read_json(mapping_index)
mappings = inventory.fetch('mappings')
expected_pending = offerings.flat_map do |_, _, resource|
  code = resource.fetch('descriptor').fetch('code')
  resource.fetch('resourceAttributes').fetch('actions', []).map do |action|
    name, ref = action.values_at('action', 'operationRef')
    next if mappings.any? { |m| m.fetch('descriptor_codes').include?(code) && m.fetch('action') == name && m.fetch('operationRef', ref) == ref }
    [code, name, ref]
  end.compact
end
recorded_pending = inventory.fetch('pending').map { |row| row.values_at('descriptor_code', 'action', 'operationRef') }
raise 'Catalog action coverage changed: update the external mappings index' unless expected_pending.sort == recorded_pending.sort
mapping_nav = mapping_index.file? ? "<li>#{link('Mapping index JSON', relative(mapping_index))}</li>" : ''
by_name = offerings.sort_by { |_, _, resource| resource.fetch('descriptor').fetch('name').downcase }
rows = by_name.map do |_, catalog, resource|
  desc = resource.fetch('descriptor')
  attrs = resource.fetch('resourceAttributes')
  provider = catalog.fetch('provider')
  "<tr><td>#{link(desc.fetch('name'), "#cap-#{desc.fetch('code')}")}</td>" \
    "<td>#{link(provider.fetch('descriptor').fetch('name'), "##{provider.fetch('id')}")}</td>" \
    "<td><code>#{escape(attrs.fetch('@type'))}</code></td></tr>"
end.join("\n")
provider_index = providers.map do |_, catalog|
  provider = catalog.fetch('provider')
  "<li>#{link(provider.fetch('descriptor').fetch('name'), "##{provider.fetch('id')}")}</li>"
end.join("\n")

provider_sections = providers.map do |file, catalog|
  provider = catalog.fetch('provider')
  resources = catalog.fetch('resources').map do |resource|
    descriptor = resource.fetch('descriptor')
    "<li>#{link(descriptor.fetch('name'), "#cap-#{descriptor.fetch('code')}")}</li>"
  end.join
  <<~HTML
    <section>
      <h3 id="#{escape(provider.fetch('id'))}">#{escape(provider.fetch('descriptor').fetch('name'))}</h3>
      <p>Catalog <code>#{escape(catalog.fetch('id'))}</code>. #{link('Read the catalog/publish fixture', relative(file))}.</p>
      <ul>#{resources}</ul>
    </section>
  HTML
end.join("\n")

capability_sections = by_name.map do |file, catalog, resource|
  provider = catalog.fetch('provider')
  desc = resource.fetch('descriptor')
  attrs = resource.fetch('resourceAttributes')
  code = desc.fetch('code')
  type = attrs.fetch('@type')
  mode = attrs.fetch('informationMode')
  search_dir = ROOT.join('api/external/knowledge/search/v0.2/examples') if code == 'knowledge-search'
  discovery = sample('Structured discovery request', search_dir ? read_json(search_dir.join('discover.json')) : DiscoveryExample.for(attrs, ROOT))
  if search_dir
    discovery += sample('Provider search request and hits', read_json(search_dir.join('search-exchange.json')).reject { |key,_| key == 'binding' })
    discovery += sample('on_discover: ranked Direct resources', read_json(search_dir.join('on_discover.json')))
  end
  notes = if catalog.fetch('resources').count { |item| item.fetch('resourceAttributes').fetch('@type') == type } > 1
            '<p>Other resources in this catalog use the same type. The binding key alone does not identify the selected resource.</p>'
          else
            ''
          end
  actions = attrs['actions'] || []
  operations = actions.map do |action|
    name, path, id, kind, href, contract = operation(action)
    "<tr><td><code>#{escape(name)}</code></td><td>#{link(id, href)}<br><code>#{escape(path)}</code>#{contract}</td>" \
      "<td>#{escape(kind)}</td></tr>"
  end
  action_table = if operations.empty?
                   '<p>No follow-up action is advertised.</p>'
                 else
                   <<~TABLE
                     <div class="table-wrap" tabindex="0" role="region" aria-label="Actions for #{escape(desc.fetch('name'))}"><table>
                       <thead><tr><th scope="col">Advertised action</th><th scope="col">OpenAPI operation</th><th scope="col">Contract</th></tr></thead>
                       <tbody>#{operations.join}</tbody>
                     </table></div>
                   TABLE
                 end
  docs = desc.fetch('docs', []).map do |doc|
    "<li>#{link(doc.fetch('label'), relative(spec_path(doc.fetch('url'))))}</li>"
  end
  upstream = desc.fetch('docs', []).map do |doc|
    file = spec_path(doc.fetch('url'))
    spec = YAML.safe_load(file.read, permitted_classes: [Date, Time], aliases: true)
    next unless spec.dig('info','x-contract-role') == 'provider-native'
    items = spec.fetch('paths').flat_map do |route, entry|
      entry.map do |method, op|
        next unless op.is_a?(Hash) && op['operationId']
        binding = op.fetch('x-oan-binding', {})
        actions = Array(binding['actions'] || binding['action']).join(', ')
        "<li><code>#{escape(method.upcase + ' ' + route)}</code>#{actions.empty? ? '' : ' · ' + escape(actions)}</li>"
      end.compact
    end
    "<p>#{link(spec.fetch('info').fetch('title'), relative(file))}</p><ul>#{items.join}</ul>"
  end.compact
  direct_links = direct.map { |target, candidate, label| link(label, relative(target)) if type == candidate }.compact
  mapping_links = mappings.select { |entry| entry.fetch('descriptor_codes').include?(code) }.map do |entry|
    path = entry.fetch('path')
    raise "Invalid mapping path #{path}" unless path.match?(%r{\A(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+\.ya?ml\z}) &&
                                                (path.split('/') & %w[. ..]).empty?

    target = mapping_directory.join(path)
    raise "Missing mapping file #{path}" unless target.file?

    "<li>#{link("#{entry.fetch('action')} · #{entry.fetch('status')} · #{File.basename(path, '.yaml')} mapping", relative(target))}</li>"
  end
  <<~HTML
    <article class="capability" id="cap-#{escape(code)}" tabindex="-1">
      <h3>#{link(desc.fetch('name'), "#cap-#{code}")}</h3>
      <div class="capability-detail">
      <p>#{link(provider.fetch('descriptor').fetch('name'), "##{provider.fetch('id')}")} · <code>#{escape(type)}</code></p>
      <p>#{escape(desc.fetch('shortDesc'))}</p>
      <h4>Registry binding example</h4>
      <p>Illustrative key: <code>#{escape("#{provider.fetch('id')}|#{type}")}</code>. This is not a registry export.</p>
      #{notes}
      <h4>Published catalog fixture</h4>
      <p><code>#{escape(catalog.fetch('id'))}</code> contains <code>#{escape(resource.fetch('id'))}</code> in <code>#{escape(mode)}</code> mode. #{link('Read the catalog/publish fixture', relative(file))}.</p>
      #{sample('Catalog resource', resource)}
      <h4>Structured discovery</h4>
      #{discovery}
      #{direct_links.empty? ? '' : "<p>Separate Direct examples for this type: #{direct_links.join(', ')}.</p>"}
      <h4>Actions and mappings</h4>
      #{upstream.empty? ? '<p>No provider HTTP contract is evidenced for this listing.</p>' : '<h5>Provider HTTP contracts and examples</h5>' + upstream.join}
      #{inventory.fetch('integrationNotes', {})[code] ? '<p>' + escape(inventory['integrationNotes'][code]) + '</p>' : ''}
      #{action_table}
      #{docs.empty? ? '' : "<ul>#{docs.join}</ul>"}
      #{mapping_links.empty? ? '<p>No mapping is linked for this capability.</p>' : "<ul>#{mapping_links.join}</ul>"}
      <p><a href="#capabilities">Back to capability index</a></p>
      </div>
    </article>
  HTML
end.join("\n")

OUTPUT.dirname.mkpath
OUTPUT.write((<<~HTML).gsub(/^[ \t]+$/, ''))
  ---
  layout: null
  permalink: /api/providers/index.html
  ---
  <!doctype html>
  <!-- Generated from provider fixtures. Regenerate: ruby scripts/generate-provider-walkthrough.rb -->
  <html lang="en">
  <head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Provider examples: catalog to action</title>
  <style>
    :root { color-scheme: light dark; }
    body { margin: 0; font: 1rem/1.55 system-ui, sans-serif; }
    main { padding: clamp(1rem, 4vw, 3.5rem); }
    a { text-underline-offset: .18em; }
    a:focus-visible, summary:focus-visible, [tabindex]:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
    h1, h2, h3, h4 { line-height: 1.2; }
    h1 { font-size: clamp(2rem, 6vw, 3.5rem); }
    h2 { margin-top: 2.5rem; }
    h4 { margin-bottom: .4rem; }
    p { max-width: 80ch; overflow-wrap: anywhere; }
    nav ul { display: flex; flex-wrap: wrap; gap: .6rem 1.5rem; list-style: none; padding: 0; }
    .providers { columns: 15rem; padding-left: 1.25rem; }
    .providers li { break-inside: avoid; }
    .table-wrap { overflow: auto; }
    table { border-collapse: collapse; width: 100%; text-align: left; }
    th, td { vertical-align: top; padding: .35rem .6rem; border-bottom: 1px solid GrayText; overflow-wrap: anywhere; }
    details { margin: .75rem 0; }
    summary { cursor: pointer; }
    pre { overflow: auto; padding: 1rem; border: 1px solid GrayText; }
    .capability { border-top: 1px solid GrayText; padding-block: .8rem; }
    .capability h3 { margin: 0; }
    .capability-detail { display: none; }
    .capability:target .capability-detail { display: block; }
    .capability:target { scroll-margin-block: 1rem; }
    .operation li { margin-block: .4rem; }
  </style>
  </head>
  <body>
  <main id="top">
    <h1>Provider examples: catalog to action</h1>
    <p>Trace a provider capability through its catalog listing, structured discovery, and advertised actions. These fixtures describe example contracts. They do not establish a live provider, registry entry, or deployed mapping.</p>
    <nav aria-label="Page sections"><ul>
      <li><a href="#providers">Providers</a></li><li><a href="#capabilities">Capabilities</a></li>
      <li><a href="#modes">Direct and OnDemand</a></li>#{mapping_nav}
    </ul></nav>
    <h2 id="modes">Direct and OnDemand</h2>
    <p>For a <code>Direct</code> resource, the record is already in the discovery result. Reading that record needs no follow-up action. An <code>OnDemand</code> resource advertises what the provider can return or do. The client uses an advertised action to get the result or start the workflow.</p>
    <p>The registry and catalog answer different questions. The catalog advertises what the provider offers. The registry binds actions to handlers. Native operation links below identify upstream HTTP contracts, not network action endpoints.</p>
    <ul>#{direct.map { |file, _, name| "<li>#{link(name, relative(file))}</li>" }.join}</ul>
    <h2 id="providers">Provider index</h2>
    <ul class="providers">#{provider_index}</ul>
    <h2 id="capabilities">Capability index</h2>
    <div class="table-wrap" tabindex="0" role="region" aria-label="Capability index"><table>
      <thead><tr><th scope="col">Capability</th><th scope="col">Provider</th><th scope="col">Resource type</th></tr></thead>
      <tbody>#{rows}</tbody>
    </table></div>
    <h2>Provider catalogs</h2>
    #{provider_sections}
    <h2>Capability walkthroughs</h2>
    #{capability_sections}
    <p><a href="#top">Back to top</a></p>
  </main>
  </body>
  </html>
HTML
