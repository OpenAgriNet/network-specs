#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "pathname"

ROOT = Pathname.new(__dir__).join("..").expand_path
SCHEMA_DATA = ROOT.join("_data", "schema_packs.json")
DATE_FORMAT = /format: "(?:date|date-time)"/
# A pack states the container it rides in: one for a domain pack, one per action
# for a provider API pack. "channels" is the only name that is not the path it
# maps to, so an unknown name is an error rather than a guess.
CONTAINER_PREFIXES = {
  "resourceAttributes" => "beckn:resourceAttributes",
  "commitmentAttributes" => "beckn:commitmentAttributes",
  "channels" => "beckn:support.channels[0]"
}.freeze

# A path belongs to a root when it is that root or sits under it.
def rooted_in?(path, roots)
  roots.any? do |root|
    path == root || path.start_with?("#{root}.") || path.start_with?("#{root}[]")
  end
end

unless SCHEMA_DATA.file?
  warn "Missing #{SCHEMA_DATA.relative_path_from(ROOT)}. Run scripts/generate-schema-pages.rb first."
  exit 1
end

errors = []
packs = JSON.parse(SCHEMA_DATA.read)

packs.each_value do |pack|
  profile_path = ROOT.join("schema", pack.fetch("name"), pack.fetch("version_dir"), "profile.json")
  profile = JSON.parse(profile_path.read)
  label = "#{pack.fetch('name')}/#{pack.fetch('version_dir')}"

  indexable = profile.fetch("indexable_paths")
  filterable = profile.fetch("filterable_paths")
  sortable = profile.fetch("sortable_paths")
  composed_paths = pack.fetch("fields").map { |field| field.fetch("path") }

  containers = (pack["beckn_container_by_action"]&.values ||
                [pack.fetch("beckn_container", "resourceAttributes")]).uniq
  unknown = containers.reject { |container| CONTAINER_PREFIXES.key?(container) }
  unless unknown.empty?
    errors << "#{label}: unknown Beckn container: #{unknown.join(', ')}"
    next
  end
  prefixes = containers.map { |container| "#{CONTAINER_PREFIXES.fetch(container)}." }

  {
    "indexable_paths" => indexable,
    "filterable_paths" => filterable,
    "sortable_paths" => sortable
  }.each do |field, paths|
    duplicates = paths.group_by(&:itself).select { |_, values| values.length > 1 }.keys
    errors << "#{label}: #{field} contains duplicates: #{duplicates.join(', ')}" unless duplicates.empty?

    invalid = paths.reject { |path| prefixes.any? { |prefix| path.start_with?(prefix) } }
    unless invalid.empty?
      errors << "#{label}: #{field} contains paths outside the pack's containers " \
                "(#{prefixes.join(', ')}): #{invalid.join(', ')}"
    end

    unrooted = paths.each_with_object([]) do |path, result|
      prefix = prefixes.find { |candidate| path.start_with?(candidate) }
      next unless prefix

      result << path unless rooted_in?(path.delete_prefix(prefix), composed_paths)
    end
    errors << "#{label}: #{field} contains paths not rooted in the composed schema: #{unrooted.join(', ')}" unless unrooted.empty?
  end

  missing_filter_indexes = filterable - indexable
  unless missing_filter_indexes.empty?
    errors << "#{label}: filterable paths must also be indexable: #{missing_filter_indexes.join(', ')}"
  end

  missing_sort_indexes = sortable - indexable
  unless missing_sort_indexes.empty?
    errors << "#{label}: sortable paths must also be indexable: #{missing_sort_indexes.join(', ')}"
  end

  # Only a date the pack hands back is a query dimension; an inbound-only field or a
  # credential timestamp is neither. A pack that lists no result fields keeps every date.
  result_fields = profile["result_fields"]
  # Indexed under any one container is enough: a field never appears in every call.
  date_paths = pack.fetch("fields")
                   .select { |field| field.fetch("constraints", "").match?(DATE_FORMAT) }
                   .select { |field| result_fields.nil? || rooted_in?(field.fetch("path"), result_fields) }
                   .map { |field| prefixes.map { |prefix| "#{prefix}#{field.fetch('path')}" } }

  missing_date_indexes = date_paths.reject { |candidates| candidates.any? { |path| indexable.include?(path) } }
  unless missing_date_indexes.empty?
    errors << "#{label}: date fields must be indexable under one of the pack's containers: " \
              "#{missing_date_indexes.map { |candidates| candidates.join(' or ') }.join('; ')}"
  end

  missing_date_filters = date_paths.reject { |candidates| candidates.any? { |path| filterable.include?(path) } }
  unless missing_date_filters.empty?
    errors << "#{label}: date fields must be filterable under one of the pack's containers: " \
              "#{missing_date_filters.map { |candidates| candidates.join(' or ') }.join('; ')}"
  end
end

if errors.empty?
  puts "Profile path audit passed for #{packs.length} schema packs."
  exit 0
end

warn errors.map { |error| "- #{error}" }.join("\n")
exit 1
