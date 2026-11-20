require 'json'

# One example envelope; select public filter values from the catalog listing.
module DiscoveryExample
  def self.for(attrs, root, capability_dir)
    template = root.join('schema/Grievance/v0.2/examples/pmfby/pmfby-grievances/discover-request.json')
    request = JSON.parse(template.read)
    callback = capability_dir.join('on-discover.json')
    if callback.file?
      ctx = JSON.parse(callback.read).fetch('context')
      request['context'].merge!(ctx.slice('transactionId', 'messageId', 'timestamp'))
    end
    request['context']['schemaContext'] = [attrs.fetch('@context') + '#' + attrs.fetch('@type')]
    fields = {'"@type"' => attrs.fetch('@type'), 'informationMode' => attrs.fetch('informationMode'),
              'subjectCategories[*]' => attrs.fetch('subjectCategories', []).first,
              'scheme.code' => attrs.dig('scheme', 'code'),
              'supportedFacilityTypes[*]' => attrs.fetch('supportedFacilityTypes', []).first}
    predicates = fields.compact.map { |key,val| "@.resourceAttributes.#{key} == #{val.to_json}" }
    request['message']['intent']['filters']['expression'] = "$.catalogs[*].resources[*] ? (#{predicates.join(' && ')})"
    request
  end
end
