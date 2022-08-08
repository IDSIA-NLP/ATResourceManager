#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: ...
Author: ...
Month Year
"""
# --------------------------------------------------------------------------------------------
#                                           IMPORT
# --------------------------------------------------------------------------------------------

import argparse
from loguru import logger
import json
from bs4 import BeautifulSoup
import glob
import os
import requests
import copy

# --------------------------------------------------------------------------------------------
#                                            MAIN
# --------------------------------------------------------------------------------------------


# ----------------------------------------- Functions ----------------------------------------
class EvalDataloader:
    """Create evaluation datasets from the gold annotations.
    """
    def __init__(self, logger, args):
        self.logger = logger
        self.args = args
        self.anno_legend = self.load(self.args.anno_legend_file, "json")

        self.annotator = None
        self.doc_filename = None
        self.anno_data = None
        self.doc_sections = None
        self.pmcid = None

    def load(self, filename, file_type):
        """Load .html or the corresponding annotation .json files.

        Args:
            filename (str): The full path to the file.
            file_type (str): Flag for the file type.

        Returns:
            dict: Data dictionary
        """
        if file_type == "json":
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        if file_type == "html":
            with open(filename, encoding="utf8") as f:
                soup = BeautifulSoup(f, "lxml")
            return soup

    def get_pmcid(self, doi):
        """Request the PMCID from PMC.

        Args:
            doi (str): DOI string.

        Returns:
            str: PMCID string.
        """
        try:
            res = requests.get(f'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi}&format=json')
            return res.json()["records"][0]["pmcid"]
        except:
            return ""


    def get_relation_name(self, ent1, ent2):
        """Get the relation name for two entities.

        Args:
            ent1 (str): Name of the first entity.
            ent2 (str): Name of the second entity.

        Returns:
            str: The relation name.
        """
        if set([ent1, ent2]) == set(["Arthropod", "Trait"]):
            return "hasTrait"
        if set([ent1, ent2]) == set(["Trait", "Value"]):
            return "hasValue"
        if "Qualifier" in [ent1, ent2]:
            return "hasQualifier"
        if  ent1 == ent2:
            return "hasContinuation"
        return "undefined"

    def get_rel_entity(self, ent_str, ent_list):
        """Find entity in entity list.

        Args:
            ent_str (str): Entity string.
            ent_list (list): List of entities.

        Returns:
            dict: Entity dictionary.
        """
        part, classId, offset = ent_str.split("|")
        start, end = offset.split(",")
        for ent in ent_list:
            ent_end = ent['offset']['start'] + ent['offset']['len'] - 1 
            if ent["classId"] == classId and ent["part"] == part and ent['offset']['start'] == int(start) and  ent_end == int(end):
                return ent    
        return None
        
    def convert_anno(self, data):
        """Convert annotations to desired output format.

        Args:
            data (dict): Annotation data.

        Returns:
            dict: Converted annotations.
        """
        annos = {
            "doc_id" : data['sources'][0]['id'],
            "doc_url" : data['sources'][0]['url'],
            "completed" : data['anncomplete']
        }
        new_ents = []
        for idx, ent in enumerate(data['entities']):
            new_ents.append({
                'id': str(idx),
                'name': self.anno_legend[ent['classId']],
                'classId': ent['classId'],
                'part': ent["part"],
                'offset': {
                    "start": ent["offsets"][0]["start"],
                    "len": len(ent["offsets"][0]["text"])
                },
                'text': ent["offsets"][0]["text"],
                'annotator': self.annotator
            })
            
        new_rels = []
        for idx, rel in enumerate(data['relations']):
           
            ent_1 = self.get_rel_entity(rel['entities'][0], new_ents)
            ent_2 = self.get_rel_entity(rel['entities'][1], new_ents)
           
            if ent_1 and ent_2:
                rel_name = self.get_relation_name(ent_1["name"], ent_2["name"])

                new_rels.append({
                    'id': str(idx),
                    'name': rel_name,
                    'classId': rel['classId'],
                    'type': 'linked',
                    'directed': False,
                    'entities': [ent_1["id"], ent_2["id"]],
                    'annotator': self.annotator
                })
            else:
                print("Couldn't find entities") 
        
        annos["entities"] = new_ents
        annos["relations"] = new_rels
        
        return annos

    def get_section(self, id_str):
        """Check format and get section.

        Args:
            id_str (str): Section ID string.

        Returns:
            str: Section string.
        """
        section = ""
        for idx, c in enumerate(id_str):
            if idx == 0 and c != "s":
                print("Male formatted!")
                return None
            
            if idx > 0 and not c.isdigit():
                return section
            
            section += c

    def get_sections(self, soup):
        """Get sections for elements in the html file.

        Args:
            soup (BeautifulSoup Obejct): The article html document in form of a BeautifulSoup object.

        Returns:
            dict: Sections of the HTML article.
        """
        sections = {}
        elements = soup.find_all(["h2","p"])
        for elem in elements:
            try: 
                sections[self.get_section(elem["id"])] += [{
                    "id": elem["id"],
                    "text": elem.text,
                    "entities": []
                }]
            except:
                sections[self.get_section(elem["id"])] = [{
                    "id": elem["id"],
                    "text": elem.text,
                    "entities": []
                }]

        return sections

    def create_bioc_json(self):
        """Create a dict to write a JSON file in BioC format.

        Returns:
            dict: Dictionary in BioC format.
        """

        out_doc = {
            'id': self.anno_data["doc_id"],
            'infons': {
                "doc_id": self.anno_data["doc_id"],
                "doc_url": self.anno_data["doc_url"],
                "doc_filename": self.doc_filename,
                "pmcid": self.pmcid
            },
            'passages': [],
            'relations': [],
        }

        doc_text_len = 0
        for idx, k in enumerate(self.doc_sections.keys()):
            psg_text = ''
            psg_start = doc_text_len
            psg_annotations = []
            for idx, s in enumerate(self.doc_sections[k]):
                

                sec_entities = []
                for e in s['entities']:
                    #e['offset']["start"] += doc_text_len
                    entity_start_char = e['offset']["start"] + doc_text_len + len(psg_text)
                    

                    entity = {}
                    entity["infons"] = {
                        "name": e['name'],
                        "classId": e['classId'],
                        "part": e['part'],
                        "annotator": e['annotator']
                    }
                    entity["text"] = e['text']
                    entity["locations"] = [{"offset": entity_start_char ,"length": e['offset']["len"]}]
                    entity["id"] = e['id']
                    sec_entities.append(entity)

                psg_text += s['text'] + '\n'
                psg_annotations += sec_entities
            
            doc_text_len += len(psg_text)

            # add annotations and relations to output dict
            out_doc["passages"].append({
                "id": str(idx),
                "infons": {
                    "part": k,
                },
                "text": psg_text,
                "offset":psg_start,
                "annotations": psg_annotations,
                "relations":[],
                "sentences":[]
            })

        
        for rel in self.anno_data["relations"]:
            ent_0_role = self.anno_data["entities"][int(rel["entities"][0])]["name"]
            assert self.anno_data["entities"][int(rel["entities"][0])]["id"] == rel["entities"][0], "Entities doesn't match"
            
            ent_1_role = self.anno_data["entities"][int(rel["entities"][1])]["name"]
            assert self.anno_data["entities"][int(rel["entities"][1])]["id"] == rel["entities"][1], "Entities doesn't match"
            
            out_doc["relations"].append({
                "id": rel["id"],
                "node": [
                    {
                        "role": ent_0_role, 
                        "refid": rel["entities"][0]
                    },
                    {
                        "role": ent_1_role, 
                        "refid": rel["entities"][1]
                    }
                ],
                "infons": {
                    "type": rel["name"],
                    "context_start_char": 0,
                    "context_end_char": doc_text_len-1,
                    "classId": rel["classId"],
                    "annotator": rel['annotator']
                }
            })

            
        return out_doc

    def create_out_json(self):
        """Create the self defined JSON dict.

        Returns:
            dict: Dictionary in self defined format.
        """
        
        out_doc = { 
            "doc_id": self.anno_data["doc_id"],
            "doc_url": self.anno_data["doc_url"],
            "doc_filename": self.doc_filename,
            "doc_pmcid": self.pmcid,
            "sections": [],
            "relations": self.anno_data["relations"]
        }

        for idx, k in enumerate(self.doc_sections.keys()):
            sec_text = ''
            sec_entities = []
            for idx, s in enumerate(self.doc_sections[k]):

                new_entities = []
                for e in s['entities']:
                    new_entity = copy.deepcopy(e)
                    new_entity['offset']["start"] += len(sec_text)
                    new_entity['line_nr'] = idx
                    new_entities.append(new_entity)

                sec_text += s['text'] + '\n'
                sec_entities += new_entities
                
            out_doc["sections"].append({
                "sec_id": str(idx),
                "part": k,
                "text": sec_text,
                "entities": sec_entities
            })

        return out_doc

    def write(self, file_type):
        """Write dictionary to self-defined JSON or to BioC JSON

        Args:
            file_type (str): Flag thats indicates the file format.
        """
        if file_type == "bioc":
            out_data = self.create_bioc_json()
            out_file = f"{self.args.out_dir}json_bioc/{self.annotator}/{self.doc_filename}.bioc.json" 

        if file_type == "json":
            out_data = self.create_out_json()
            out_file = f"{self.args.out_dir}json/{self.annotator}/{self.doc_filename}.json" 
        
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(out_data, f, ensure_ascii=False, indent=4)


    def run(self):
        """Run the evaluation dataset creation.

        Args:
            logger (loguru object): Loguru logger.

        Returns:
            None: None
        """

        self.logger.info(f'Loading documents ...')
        for filename in glob.glob(self.args.anno_dir + '*/pool/*'):
            self.annotator =  filename.split("/")[-3]
            self.doc_filename = ".".join(filename.split("/")[-1].split(".")[:-2])

            self.logger.info(f'PROCESSING FILE: {self.doc_filename} (annoted by {self.annotator})')

            anno_data = self.load(filename, "json")

            html_file = self.doc_filename + ".plain.html"
            soup = self.load(self.args.html_dir + html_file, "html")

            self.logger.info(f'Converting annotations ...')
            anno_data = self.convert_anno(anno_data)

            self.logger.info(f'Extracting HTML sections ...')
            sections = self.get_sections(soup)

            self.logger.info(f'Merging annotation entities with sections ...')
            for ent in anno_data['entities']:
                for elem in sections[self.get_section(ent['part'])]:
                    if elem['id'] == ent['part']:
                        elem['entities'].append(ent)
                        break
            
            self.anno_data = anno_data
            self.doc_sections = sections
            
            self.pmcid = self.get_pmcid( self.anno_data["doc_url"].lstrip("http://doi.org/") )
            
            self.logger.info(f'Converting to output format and writing to file...')
            
            self.write("json")
            self.write("bioc")
            
            
        return 


# --------------------------------------------------------------------------------------------
#                                          RUN
# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Setup logger
    logger.add("./create_eval_data.log", rotation="20 MB")
    logger.info(f'Start ...')

    # Setup argument parser
    description = "Application description"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-p', '--anno_dir', metavar='anno_dir', type=str, required=False, 
                        default='../../data/gold_annotations/ann.json/members/', help='Directory to  annotations.')
    parser.add_argument('-l', '--anno_legend_file', metavar='anno_legend_file', type=str, required=False, 
                        default='../../data/gold_annotations/annotations-legend.json', help='Path to annotation legend.')
    parser.add_argument('-d', '--html_dir', metavar='html_dir', type=str, required=False, 
                        default='../../data/gold_annotations/plain.html/pool/', help='Directory of HTML documents.')
    parser.add_argument('-o', '--out_dir', metavar='out_dir', type=str, required=False, 
                        default='../../data/gold_annotations/converted/', help='Output directory.')
   

    args = parser.parse_args()
    
    # Run main
    eval_dataloader = EvalDataloader(logger, args)
    eval_dataloader.run()