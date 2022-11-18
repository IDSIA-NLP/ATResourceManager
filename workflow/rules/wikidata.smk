# vim: syntax=python tabstop=2 expandtab
# coding: utf-8
#------------------------------------------------------------------------------
# Extract information about Arthopods from Wikidata dataset.
#------------------------------------------------------------------------------
# author   : Harald Detering
# email    : harald.detering@gmail.com
# modified : 2022-11-18
#------------------------------------------------------------------------------

configfile: '../config/config.yaml' 

# Dummy rule to run sub-workflow
rule wikidata_all:
  input:
    rules.wikidata_merge_col.output
  output:
    '../results/wikidata.done',
  shell:
    """
    touch {output}
    """

rule wikidata_extract_arthro:
  """Extract wikidata records related to Arthropods."""
  input:
     wiki = config['wiki_dump_file'],
     taxa = config['col_taxa_names']
  output:
    config['wiki_arthro_file']
  log:
    '../log/wikidata_extract_arthro.log'
  benchmark:
    '../log/wikidata_extract_arthro.prf'
  shell:
    """
    python scripts/wikidata_extract_arthro_wikidata.py \
      --wikidata-file {input.wiki} \
      --arthro-file {input.taxa} \
      --outout-file {output} \
    1>{log} 2>&1
    """

rule wikidata_taxa_to_wikiid:
  """Create taxon-to-wikiID mapping."""
  input:
    wiki = config['wiki_arthro_file'],
    taxa = config['col_taxa_names']
  output:
    config['wiki_taxon_to_wikiid_file']
  log:
    '../log/wikidata_taxa_to_wikiid.log'
  benchmark:
    '../log/wikidata_taxa_to_wikiid.prf'
  shell:
    """
    python scripts/wikidata_create_taxonomic_to_wiki_id.py \
      --arthro-file {input.wiki} \
      --taxo-file {input.taxa} \
      --taxo-to-wiki-file {output} \
    1>{log} 2>&1
    """

rule wikidata_crossref:
  """Extract cross-references to other databases from Wikidata data."""
  input:
    wiki = config['wiki_arthro_file']
  output:
    refs = config['wiki_crossref_file'],
    prop = config['wiki_crossref_prop_id_file']
  log:
    '../log/wikidata_crossref.log'
  benchmark:
    '../log/wikidata_crossref.prf'
  shell
    """
    python scripts/wikidata_extract_crossref_arthro_wikidata.py \
      --arthro-file {input.wiki} \
      --crossref-file {output.refs} \
      --prop-ids-file {output.prop} \
    1>{log} 2>&1
    """

rule wikidata_crossref_stats:
  """Collect statistics about cross-references."""
  input:
    refs = config['wiki_crossref_file']
  output:
    stat = config['wiki_crossref_stats_file']
  log:
    '../log/wikidata_crossref_stats.log'
  benchmark:
    '../log/wikidata_crossref_stats.prf'
  shell
    """
    python scripts/wikidata_crossref_arthro_stats.py \
      --ref-file {input.refs} \
      --out-file {output.stat} \
    1>{log} 2>&1
    """

rule wikidata_crossref_props:
  """Extract Wikidata cross-reference properties for Arthropods."""
  input:
    wiki = config['wiki_dump_file'],
    prop = config['wiki_crossref_prop_id_file']
  output:
    plof = config['wiki_crossref_props_labels_file'],
    wpof = config['wiki_crossref_props_json_file']
  log:
    '../log/wikidata_crossref_props.log'
  benchmark:
    '../log/wikidata_crossref_props.prf'
  shell:
    """
    python scripts/wikidata_extract_props_from_wikidata.py \
      --wiki-file {input.wiki} \
      --props-file {input.prop} \
      --props-to-label-outfile {output.plof} \
      --wiki-props-outfile {output.wpof} \
    1>{log} 2>&1
    """

rule wikidata_merge_col:
  """Merge attributes extracted from Wikidata with CoL taxa info."""
  input:
    taxa = config['col_taxa_names'],
    stat = rules.wikidata_crossref_stats.output.stat,
    plif = rules.wikidata_crossref_props.output.plof,
    txid = rules.wikidata_taxa_to_wikiid.output
  output:
    prop = config['wikidata_crossref_props_count_file'],
    refs = config['wikidata_crossref_arthropds_file']
  log:
    '../log/wikidata_merge_col.log'
  benchmark:
    '../log/wikidata_merge_col.prf'
  shell:
    """
    python scripts/wikidata_merge_wikidate_col.py \
      --taxon-file {input.stat} \
      --wiki-arthro-cross-stats-file {input.stat} \
      --wiki-props-label-file {input.plif} \
      --taxon-to-wiki-file {input.txid} \
      --wiki-arthro-props-file {output.prop} \
      --taxon-wiki-file {output.refs} \
    1>{log} 2>&1
    """
