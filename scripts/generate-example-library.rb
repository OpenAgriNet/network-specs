# Generate the schema-first examples directory.
require "yaml"
require "json"
require "pathname"
require "cgi"
require "uri"
require "fileutils"
require "date"
require_relative "discovery_example"

ROOT = Pathname.new(__dir__).parent
BASE = "https://openagrinet.github.io/network-specs/"
PROTO = "https://github.com/OpenAgriNet/protocol-specifications-v2/blob/a22300aa83796cb8dfc2b63cd9dd0e36a7f4d3a1/api/v2.0.0/beckn.yaml"
def h(x); CGI.escapeHTML(x.to_s); end
def rel(from, to); to.relative_path_from(from.dirname).to_s; end
def write(path, text)
  return if path.file? && path.read == text
  path.dirname.mkpath
  path.write(text)
end
def page(path, title, body)
  write(path, "---\nlayout: default\npermalink: /schema/examples/\ntitle: #{title.to_json}\n---\n<h1>#{h title}</h1>\n#{body}\n")
end
def example(media)
  return media["example"] if media.key?("example")
  media.fetch("examples", {}).each_value { |entry| return entry["value"] if entry.key?("value") }
  nil
end
def pointer(path, verb)
  "#/paths/" + URI::DEFAULT_PARSER.escape(path.gsub("~","~0").gsub("/","~1"), /[^a-zA-Z0-9~._-]/) + "/" + verb
end

ops = {}
payload_refs = {}
ROOT.glob("api/external/*/*/v0.2/openapi.yaml").sort.each do |file|
  spec = YAML.safe_load(file.read, permitted_classes: [Date, Time], aliases: true)
  spec.fetch("paths").each do |route, item|
    item.each do |verb, op|
      next unless op.is_a?(Hash) && op["operationId"]
      id = op.fetch("operationId")
      ref = BASE + file.relative_path_from(ROOT).to_s + pointer(route, verb)
      req = op.dig("requestBody","content") || {}
      responses = op.fetch("responses")
      inputs = (item.fetch("parameters", []) + op.fetch("parameters", [])).map do |p|
        p = spec.fetch("components").fetch("parameters").fetch(p.fetch("$ref").split("/").last) if p.key?("$ref")
        ["#{p.fetch('in')} parameter: #{p.fetch('name')}", p.fetch("schema")]
      end
      req.each { |mime,m| inputs << ["request: #{mime}",m.fetch("schema")] }
      responses.each { |status,b| b.fetch("content",{}).each { |mime,m| inputs << ["response #{status}: #{mime}",m.fetch("schema")] } }
      payload_refs[ref] = inputs.map do |label,schema|
        fragment = schema.fetch("$ref")
        raise "Missing named schema: #{id} #{fragment}" unless fragment.start_with?("#/components/schemas/") && spec.dig("components","schemas").key?(fragment.split("/").last)
        [label,fragment]
      end
      result = responses.find { |status, _| status.to_s.start_with?("2") }
      reply = result && (result.last["content"] || {}).values.map { |m| example(m) }.compact.first
      sample = req.values.map { |m| example(m) }.compact.first
      ops[ref] = [file, id, sample, reply, route, verb, op, file]
    end
  end
end

entries = Hash.new { |hash, key| hash[key] = [] }
root_index = ROOT.join("schema/examples/index.html")
ROOT.glob("schema/*/v0.2/examples/*/catalog.json").sort.each do |publication|
  envelope = JSON.parse(publication.read)
  envelope.fetch("message").fetch("catalogs").each do |catalog|
    catalog.fetch("resources").each do |resource|
      attrs = resource.fetch("resourceAttributes")
      pack = attrs.fetch("@type").split(":").last
      code = resource.fetch("descriptor").fetch("code")
      provider = publication.dirname.basename.to_s
      raise "Unsafe example path" unless [pack,code,provider].all? { |x| x.match?(/\A[a-zA-Z0-9-]+\z/) }
      directory = ROOT.join("schema",pack,"v0.2/examples",provider,code)
      name = resource.fetch("descriptor").fetch("name")
      entries[pack] << [provider,name,directory,code]
      native = ops.select { |_, row| row[6].dig("x-oan-binding","descriptorCode") == code }
      advertised = native.select { |_,row| attrs.fetch("actions",[]).any? { |a| a["operationRef"] == BASE + row.last.relative_path_from(ROOT).to_s + pointer(row[4],row[5]) } }
      # A terminal upstream operation may sit behind an existing adapter proposal.
      # An OTP verifier, lookup prerequisite or blocker check is not a second public action.
      terminals = {"pmfby-grievances"=>%w[filePmfbyGrievance readPmfbyGrievance],
        "pm-kisan-grievances"=>%w[sendPmkisanGrievanceOtp readPmkisanGrievance filePmkisanGrievance],
        "pm-kisan-benefits"=>%w[sendPmkisanApplicationOtp readPmkisanApplication],
        "smam-benefits"=>%w[readSmamBenefitStatus],"pocra-facilities"=>%w[searchPocraFacilities]}
      advertised = native.select { |_,row| terminals[code].include?(row[1]) } if terminals.key?(code)
      actions = advertised.map { |ref,row| {"action"=>row[6].fetch("x-oan-binding").fetch("action"),"operationRef"=>ref} }
      if !actions.empty? || attrs["informationMode"] == "Direct"
        listing = Marshal.load(Marshal.dump(envelope))
        sample_resource = Marshal.load(Marshal.dump(resource))
        sample_resource["resourceAttributes"].delete("actions")
        sample_resource["resourceAttributes"]["actions"] = actions unless actions.empty?
        sample_resource["descriptor"]["docs"] = advertised.values.map(&:last).uniq.map { |f| {"label"=>"Provider HTTP contract","url"=>BASE + f.relative_path_from(ROOT).to_s,"mimeType"=>"application/vnd.oai.openapi"} }
        advertised.each do |ref,row|
          payload_refs.fetch(ref).each do |label,fragment|
            sample_resource["descriptor"]["docs"] << {"label"=>"#{row[1]} · #{label}", "url"=>ref.split("#").first+fragment, "mimeType"=>"application/vnd.oai.openapi"}
          end
        end
        listing["message"]["catalogs"] = [catalog.merge("resources"=>[sample_resource])]
        write(directory.join("publish.json"), JSON.pretty_generate(listing)+"\n")
      end
      if code == "pmfby-grievances"
        ref,row = advertised.find { |_,r| r[1]=="readPmfbyGrievance" }
        context = {"domain"=>"agriculture","version"=>"2.0.0","action"=>"status","transactionId"=>"00000000-0000-4000-8000-000000000001","messageId"=>"00000000-0000-4000-8000-000000000002","timestamp"=>"2026-10-12T12:00:00Z","bapId"=>"consumer.example.invalid","bapUri"=>"https://consumer.example.invalid/beckn","bppId"=>catalog["bppId"],"bppUri"=>catalog["bppUri"],"ttl"=>"PT30S"}
        [ ["status",row[2]],["on_status",row[3]] ].each do |action,payload|
          at = {"@context"=>BASE+"schema/examples/provider-payload/context.jsonld","@type"=>"ProviderOperationPayload","operationRef"=>ref,"payload"=>payload}
          commitment = {"id"=>"example-commitment","status"=>{"descriptor"=>{"code"=>"ACTIVE"}},"resources"=>[{"id"=>resource["id"],"quantity"=>{"value"=>1}}],"offer"=>{"id"=>"example-offer","resourceIds"=>[resource["id"]]},"commitmentAttributes"=>at}
          wire = {"context"=>context.merge("action"=>action),"message"=>{"contract"=>{"id"=>"00000000-0000-4000-8000-000000000003","commitments"=>[commitment]}}}
          write(directory.join(action+".json"),JSON.pretty_generate(wire)+"\n")
        end
        recipe = {"exampleOnly"=>true,"participant"=>catalog['bppId'],"capability"=>attrs['@type'],"action"=>"status","operationRef"=>ref,"method"=>"POST","path"=>row[4],"serverRef"=>"pmfby.fgms.baseUrl","headers"=>{"Content-Type"=>"application/json","Authorization"=>{"secretRef"=>"pmfby.fgms.authorization"}},"bodyFrom"=>"message.contract.commitments[0].commitmentAttributes.payload","responseTo"=>"message.contract.commitments[0].commitmentAttributes.payload","responseGuard"=>"Release only a successful response authorized for the caller and requested ticket. Otherwise return an error without the provider body."}
        write(directory.join("adapter.example.json"),JSON.pretty_generate(recipe)+"\n")
      end
    end
  end
end
out="<p>Choose a schema, then a provider to see its discovery example, native API and adapter responsibilities. Direct resources can be read from discovery without another call.</p>"
ROOT.glob("schema/*/v0.2/attributes.yaml").each { |f| entries[f.dirname.parent.basename.to_s] }
entries.sort.each do |pack,items|
  dir=ROOT.join("schema",pack,"v0.2")
  samples=dir.join("examples").glob("*.json").select { |f| JSON.parse(f.read)["informationMode"]=="Direct" }
  out+="<details><summary><strong>#{h pack}</strong> · v0.2 · #{items.size} capabilities</summary><p><a href=\"#{rel(root_index,dir)}/\">Schema definition</a></p>"
  items.group_by(&:first).sort.each { |provider,list| out+="<h3>#{h provider}</h3><ul>"+list.map { |_,name,d,code|
    files=d.glob("*.json").sort
    links=files.map { |f| "<a href=\"#{rel(root_index,f)}\">#{h f.basename('.json')}</a>" }
    links << "<a href=\"providers/index.html#cap-#{h code}\">Walkthrough</a>"
    "<li>#{h name}: #{links.join(' · ')}</li>"
  }.join+"</ul>" }
  out+="<p>Direct examples: "+samples.map { |f| "<a href=\"#{rel(root_index,f)}\">#{h f.basename('.json')}</a>" }.join(" · ")+"</p>" unless samples.empty?
  out+="</details>"
end
out += "<h2>Pack fixtures by version</h2><p>These are schema-validation examples, not provider registrations.</p>"
network = Hash.new { |hash,key| hash[key]=[] }
ROOT.glob("schema/*/v*/examples/network/*.json").sort.each do |file|
  file.read.scan(%r{network-specs/schema/(\w+)/(v[\d.]+)/context\.jsonld}).uniq.each { |key| network[key] << file }
end
ROOT.glob("schema/*/v*/attributes.yaml").group_by { |f| f.dirname.parent.basename.to_s }.sort.each do |pack, versions|
  out += "<details><summary>#{h pack}</summary>"
  versions.sort.reverse_each do |f|
    examples = f.dirname.join("examples").glob("*.json") + network[[pack,f.dirname.basename.to_s]]
    out += "<h3>#{h f.dirname.basename}</h3><ul>"+examples.map { |x| "<li><a href=\"#{rel(root_index,x)}\">#{h x.basename('.json')}</a></li>" }.join+"</ul>"
  end
  out += "</details>"
end
page(ROOT.join("schema/examples.html"),"Schema examples",out)
