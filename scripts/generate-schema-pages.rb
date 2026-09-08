#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "pathname"
require "yaml"

ROOT = Pathname.new(__dir__).join("..").expand_path
SCHEMA_ROOT = ROOT.join("schema")
DATA_FILE = ROOT.join("_data", "schema_packs.json")

class SchemaResolver
  CONSTRAINT_KEYS = %w[
    const enum format pattern minLength maxLength minimum maximum
    exclusiveMinimum exclusiveMaximum minItems maxItems uniqueItems
    minProperties maxProperties additionalProperties
  ].freeze

  def initialize
    @documents = {}
  end

  def document(path)
    @documents[path.to_s] ||= YAML.safe_load(path.read, aliases: true)
  end

  def resolve(schema, source_path)
    return [schema || {}, source_path, nil] unless schema.is_a?(Hash) && schema["$ref"]

    reference = schema["$ref"]
    return [schema, source_path, reference] if reference.start_with?("http://", "https://")

    file_part, pointer = reference.split("#", 2)
    target_path = file_part.to_s.empty? ? source_path : source_path.dirname.join(file_part).cleanpath
    target = document(target_path)
    pointer.to_s.split("/").reject(&:empty?).each do |segment|
      target = target.fetch(segment.gsub("~1", "/").gsub("~0", "~"))
    end
    target = rebase_internal_refs(target, target_path)

    siblings = schema.reject { |key, _| key == "$ref" }
    [deep_merge(target, siblings), target_path, reference]
  end

  def expand(schema, source_path, seen = [])
    resolved, resolved_path, external_ref = resolve(schema, source_path)
    return [resolved, resolved_path, external_ref] if external_ref&.start_with?("http://", "https://")

    fingerprint = [resolved_path.to_s, resolved.object_id]
    return [resolved, resolved_path, nil] if seen.include?(fingerprint)

    merged = resolved.reject { |key, _| key == "allOf" }
    Array(resolved["allOf"]).each do |member|
      expanded, = expand(member, resolved_path, seen + [fingerprint])
      merged = deep_merge(merged, expanded)
    end
    [merged, resolved_path, nil]
  end

  def constraints(schema)
    CONSTRAINT_KEYS.each_with_object([]) do |key, values|
      next unless schema.key?(key)

      value = schema[key]
      formatted = value.is_a?(Array) ? value.join(", ") : value.inspect
      values << "#{key}: #{formatted}"
    end
  end

  private

  def rebase_internal_refs(value, target_path)
    case value
    when Hash
      value.each_with_object({}) do |(key, child), result|
        result[key] = if key == "$ref" && child.is_a?(String) && child.start_with?("#")
                        "#{target_path}#{child}"
                      else
                        rebase_internal_refs(child, target_path)
                      end
      end
    when Array
      value.map { |child| rebase_internal_refs(child, target_path) }
    else
      value
    end
  end

  def deep_merge(left, right)
    left.merge(right) do |key, old_value, new_value|
      if old_value.is_a?(Hash) && new_value.is_a?(Hash)
        deep_merge(old_value, new_value)
      elsif key == "required" && old_value.is_a?(Array) && new_value.is_a?(Array)
        (old_value + new_value).uniq
      elsif key == "allOf" && old_value.is_a?(Array) && new_value.is_a?(Array)
        old_value + new_value
      else
        new_value
      end
    end
  end
end

def titleize(value)
  value.to_s
       .gsub(/([a-z0-9])([A-Z])/, '\\1 \\2')
       .gsub(/[_-]+/, " ")
       .split
       .map(&:capitalize)
       .join(" ")
end

def schema_type(schema, external_ref = nil)
  return "External object" if external_ref
  return schema["type"] if schema["type"]
  return "constant" if schema.key?("const")
  return "choice" if schema["oneOf"] || schema["anyOf"]

  "object"
end

def condition_label(condition)
  values = condition.fetch("properties", {}).each_with_object([]) do |(field, rule), result|
    next unless rule.is_a?(Hash) && rule.key?("const")

    result << if %w[informationMode observationType].include?(field)
                rule["const"].to_s
              else
                "#{field}=#{rule['const']}"
              end
  end
  values.empty? ? "Conditional" : values.join(" + ")
end

def collect_conditionals(schema)
  Array(schema["allOf"]).flat_map do |member|
    next [] unless member.is_a?(Hash)

    current = []
    if member["if"] && member["then"]
      label = condition_label(member["if"])
      current.concat(Array(member.dig("then", "required")).map { |field| [field, label] })
    end
    current + collect_conditionals(member)
  end
end

def value_at(object, path)
  path.reduce(object) do |value, segment|
    return nil if value.nil?

    if segment == "[]"
      value.is_a?(Array) ? value.first : nil
    elsif value.is_a?(Hash)
      value[segment]
    end
  end
end

def concise_example(value)
  return nil if value.nil?

  rendered = JSON.pretty_generate(value)
  rendered.length > 420 ? "#{rendered[0, 417]}..." : rendered
end

def display_reference(reference)
  return reference unless reference&.start_with?(ROOT.to_s)

  path, pointer = reference.split("#", 2)
  relative_path = Pathname.new(path).relative_path_from(ROOT)
  pointer ? "#{relative_path}##{pointer}" : relative_path.to_s
end

def collect_fields(resolver, schema, source_path, examples, root_origins = {}, path = [], ancestor_condition = nil, depth = 0, inherited_origin = nil)
  return [] if depth > 5

  expanded, expanded_path, = resolver.expand(schema, source_path)
  properties = expanded.fetch("properties", {})
  required = Array(expanded["required"])
  conditional = collect_conditionals(schema).group_by(&:first).transform_values { |pairs| pairs.map(&:last) }

  properties.flat_map do |name, raw_property|
    origin = inherited_origin || root_origins[name] || expanded_path.dirname.parent.basename.to_s
    property, property_path, property_external_ref = resolver.expand(raw_property, expanded_path)
    field_path = path + [name]
    requirement = if required.include?(name)
                    ancestor_condition || "Always"
                  elsif conditional[name]&.any?
                    conditional[name].join(" or ")
                  else
                    "Optional"
                  end

    item_schema = property["items"]
    type = schema_type(property, property_external_ref)
    display_type = type == "array" ? "array<#{schema_type(item_schema || {})}>" : type
    all_of_reference = Array(raw_property["allOf"]).each_with_object([]) do |part, references|
      references << part["$ref"] if part.is_a?(Hash) && part["$ref"]
    end.first
    reference = property_external_ref || raw_property["$ref"] || all_of_reference
    sample = examples.lazy.map { |example| value_at(example["data"], field_path) }.find { |value| !value.nil? }

    row = {
      "path" => field_path.join(".").gsub(".[]", "[]"),
      "type" => display_type,
      "requirement" => requirement,
      "description" => property["description"] || raw_property["description"] || "No description supplied.",
      "constraints" => resolver.constraints(property).join(" · "),
      "reference" => display_reference(reference),
      "origin" => origin,
      "example" => concise_example(sample),
      "enum" => property["enum"] || item_schema&.dig("enum")
    }

    nested = if property["type"] == "array" && item_schema
               item_schema
             elsif property["properties"] || property["allOf"] || property["$ref"]
               property
             end
    children = if nested && !property_external_ref
                 nested_path = field_path + (property["type"] == "array" ? ["[]"] : [])
                 child_condition = if required.include?(name)
                                     ancestor_condition
                                   elsif conditional[name]&.any?
                                     conditional[name].join(" or ")
                                   else
                                     "When #{field_path.join('.')} is supplied"
                                   end
                 collect_fields(resolver, nested, property_path, examples, root_origins, nested_path, child_condition, depth + 1, origin)
               else
                 []
               end
    [row] + children
  end
end

def component_name(reference)
  return "Pack-specific constraints" unless reference

  name = reference.split("#", 2).last.to_s.split("/").last
  name.to_s.empty? ? reference : name
end

resolver = SchemaResolver.new
packs = {}

Dir.glob(SCHEMA_ROOT.join("*", "v*", "profile.json")).sort.each do |profile_file|
  profile_path = Pathname.new(profile_file)
  pack_dir = profile_path.dirname
  pack_name = pack_dir.parent.basename.to_s
  version_dir = pack_dir.basename.to_s
  profile = JSON.parse(profile_path.read)
  attributes_path = pack_dir.join("attributes.yaml")
  attributes = resolver.document(attributes_path)
  schema_name = Array(profile["included_schemas"]).first || pack_name
  root_schema = attributes.dig("components", "schemas", schema_name)
  raise "Missing schema #{schema_name} in #{attributes_path}" unless root_schema

  examples = Dir.glob(pack_dir.join("examples", "*.json")).sort.map do |file|
    path = Pathname.new(file)
    data = JSON.parse(path.read)
    {
      "name" => titleize(path.basename(".json").to_s),
      "file" => path.relative_path_from(pack_dir).to_s,
      "mode" => data["informationMode"],
      "data" => data,
      "json" => JSON.pretty_generate(data)
    }
  end

  root_origins = {}
  referenced_components = Array(root_schema["allOf"]).filter { |member| member.is_a?(Hash) && member["$ref"] }.map do |member|
    resolved_component, = resolver.expand(member, attributes_path)
    component_origin = component_name(member["$ref"]).sub(/Fields\z/, "")
    resolved_component.fetch("properties", {}).each_key { |field| root_origins[field] = component_origin }
    {
      "name" => component_name(member["$ref"]),
      "reference" => member["$ref"],
      "role" => "Shared fields"
    }
  end
  root_schema.fetch("properties", {}).each_key { |field| root_origins[field] = pack_name }
  Array(root_schema["allOf"]).reject { |member| member.is_a?(Hash) && member["$ref"] }.each do |member|
    member.fetch("properties", {}).each_key { |field| root_origins[field] = pack_name } if member.is_a?(Hash)
  end
  composition = referenced_components + [{
    "name" => "#{pack_name} fields and rules",
    "reference" => nil,
    "role" => "Pack-specific constraints"
  }]
  pack_schema = root_schema.merge(
    "allOf" => Array(root_schema["allOf"]).reject do |member|
      member.is_a?(Hash) && member["$ref"] && !member["$ref"].start_with?("#")
    end
  )

  key = "#{pack_name}-#{version_dir}"
  packs[key] = {
    "key" => key,
    "name" => pack_name,
    "display_name" => profile["name"].to_s.sub(/ Attributes\z/, ""),
    "version" => profile["version"],
    "version_dir" => version_dir,
    "protocol_version" => profile["protocol_version"],
    "interaction_type" => profile["interaction_type"],
    "description" => attributes.dig("info", "description").to_s.strip.gsub(/\s+/, " "),
    "canonical_type" => root_schema.dig("x-jsonld", "@type"),
    "schema_name" => schema_name,
    "composition" => composition,
    "pack_fields" => collect_fields(resolver, pack_schema, attributes_path, examples, {}, [], nil, 0, pack_name),
    "fields" => collect_fields(resolver, root_schema, attributes_path, examples, root_origins),
    "conditions" => collect_conditionals(root_schema).map { |field, condition| { "field" => field, "condition" => condition } },
    "examples" => examples.map { |example| example.reject { |key_name, _| key_name == "data" } },
    "artifacts" => %w[vocab.jsonld context.jsonld attributes.yaml profile.json renderer.json]
  }

  pack_dir.join("index.md").write(<<~MARKDOWN)
    ---
    layout: schema-pack
    schema_key: #{key}
    title: #{pack_name}
    permalink: /schema/#{pack_name}/#{version_dir}/
    ---
    <!-- Generated by scripts/generate-schema-pages.rb. Edit the schema artifacts, profile, or examples instead. -->
  MARKDOWN
end

DATA_FILE.dirname.mkpath
DATA_FILE.write("#{JSON.pretty_generate(packs)}\n")
puts "Generated #{packs.length} schema pages and #{DATA_FILE.relative_path_from(ROOT)}"
