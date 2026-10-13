#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "pathname"

ROOT = Pathname.new(__dir__).join("..").expand_path
SCHEMA_DATA = ROOT.join("_data", "schema_packs.json")
RESOURCE_ATTRIBUTE_PREFIX = "beckn:resourceAttributes."
DATE_FORMAT = /format: "(?:date|date-time)"/

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

  {
    "indexable_paths" => indexable,
    "filterable_paths" => filterable,
    "sortable_paths" => sortable
  }.each do |field, paths|
    duplicates = paths.group_by(&:itself).select { |_, values| values.length > 1 }.keys
    errors << "#{label}: #{field} contains duplicates: #{duplicates.join(', ')}" unless duplicates.empty?

    invalid = paths.reject { |path| path.start_with?(RESOURCE_ATTRIBUTE_PREFIX) }
    errors << "#{label}: #{field} contains paths outside resourceAttributes: #{invalid.join(', ')}" unless invalid.empty?

    unrooted = paths.each_with_object([]) do |path, result|
      next unless path.start_with?(RESOURCE_ATTRIBUTE_PREFIX)

      relative_path = path.delete_prefix(RESOURCE_ATTRIBUTE_PREFIX)
      rooted = composed_paths.any? do |composed_path|
        relative_path == composed_path ||
          relative_path.start_with?("#{composed_path}.") ||
          relative_path.start_with?("#{composed_path}[]")
      end
      result << path unless rooted
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

  date_paths = pack.fetch("fields")
                   .select { |field| field.fetch("constraints", "").match?(DATE_FORMAT) }
                   .map { |field| "#{RESOURCE_ATTRIBUTE_PREFIX}#{field.fetch('path')}" }

  missing_date_indexes = date_paths - indexable
  unless missing_date_indexes.empty?
    errors << "#{label}: date fields must be indexable: #{missing_date_indexes.join(', ')}"
  end

  missing_date_filters = date_paths - filterable
  unless missing_date_filters.empty?
    errors << "#{label}: date fields must be filterable: #{missing_date_filters.join(', ')}"
  end
end

if errors.empty?
  puts "Profile path audit passed for #{packs.length} schema packs."
  exit 0
end

warn errors.map { |error| "- #{error}" }.join("\n")
exit 1
