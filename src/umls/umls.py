import os
import requests
from utils.fileUtils import FilesUtils

class UMLS:
    def __init__(self, apikey:str = None):
        if apikey is None:
            self.umls_apikey = os.getenv('UMLS')
        else:
            self.umls_apikey = apikey
    
    def find_mesh_source_descriptor_by_term(self, term:str):
        params = {
            'apiKey': self.umls_apikey, 
            'string': term,
            'searchType': 'exact',
            'returnIdType': 'sourceDescriptor',
            'sabs': 'MSH',
            'pageSize': '1'
        }
        fallback_params = {
            'apiKey': self.umls_apikey, 
            'string': term,
            'searchType': 'words',
            'returnIdType': 'sourceDescriptor',
            'sabs': 'MSH',
            'pageSize': '1',
            'partialSearch': True
        }

        url = 'https://uts-ws.nlm.nih.gov/rest/search/current'
        response = requests.get(url=url, params=params)
        content = response.json()

        if len(content['result']['results']):
            mesh_id = content['result']['results'][0]['ui']
            return mesh_id
        else:
            try:
                response = requests.get(url=url, params=fallback_params)
                content = response.json()
                mesh_id = content['result']['results'][0]['ui']
                return mesh_id
            except:
                return None

#  -----------------Retrieve Term information------------------
    # main
    def term_info(self, mesh, bc5cdr_term):
        """
        {
            "bc5cdr_mesh_id": "D016651",
            "MSH_term": "Lithium Carbonate",
            "cui": "C0085217",
            "definition": "A lithium salt, classified as a mood-stabilizing agent. Lithium ion alters the metabolism of BIOGENIC MONOAMINES in the CENTRAL NERVOUS SYSTEM, and affects multiple neurotransmission systems.",
            "definition_source": "MSH",
            "termType": ["Pharmacologic Substance", "Inorganic Chemical"],
            "synonyms": [
                "dilithium carbonate",
                "of lithium carbonate",
                "carbonate lithium",
                "carbonate, dilithium",
                "lithii carbonas",
                "lithium carbonate (medication)",
                "carbonate, lithium",
                "lithium carbonate",
                "product containing lithium carbonate (medicinal product)",
                "carbonic acid, dilithium salt",
                "lithium carbonate (substance)",
                "lithium carbonate-containing product",
                "lithium carbonate preparation"
            ],
            "relations": [
                {
                "relation": "has_mechanism_of_action",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Norepinephrine Transporter Interactions",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MED-RT/N0000000234"
                },
                {
                "relation": "contraindicated_with_disease",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Hyponatremia",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0010911"
                },
                {
                "relation": "has_mechanism_of_action",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Serotonin Transporter Interactions",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MED-RT/N0000000167"
                },
                {
                "relation": "has_mechanism_of_action",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Unknown Cellular or Molecular Interaction",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MED-RT/N0000009915"
                },
                {
                "relation": "contraindicated_with_disease",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Drug Hypersensitivity",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0006829"
                },
                {
                "relation": "contraindicated_with_disease",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Coronary Disease",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0005191"
                },
                {
                "relation": "contraindicated_with_disease",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Dehydration",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0005757"
                },
                {
                "relation": "may_treat",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Depressive Disorder",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0006033"
                },
                {
                "relation": "may_treat",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Bipolar Disorder",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0002571"
                },
                {
                "relation": "may_treat",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Conduct Disorder",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0029628"
                },
                {
                "relation": "contraindicated_with_disease",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Pregnancy",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0017471"
                },
                {
                "relation": "may_treat",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Stress Disorders, Post-Traumatic",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0020602"
                },
                {
                "relation": "contraindicated_with_disease",
                "entity_1_name": "lithium carbonate",
                "entity_1_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/RXNORM/42351",
                "entity_2_name": "Kidney Diseases",
                "entity_2_uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/M0012014"
                }
            ]
        }
        """
        map_output = {
            "bc5cdr_mesh_id": mesh,
        }

        # ---------------------------1------------------------------
        bc5cdrMesh_to_MSHTerm = self.bc5cdrMesh_to_MSHTerm(mesh=mesh, bc5cdr_term=bc5cdr_term)
        try:
            MSHTerm = bc5cdrMesh_to_MSHTerm['name']
            map_output["MSH_term"] = MSHTerm
        
        except:
            print(mesh)
            MSHTerm = bc5cdr_term
            map_output["MSH_term"] = MSHTerm

        # ---------------------------2------------------------------
        MSHTerm_to_Cui = self.MSHTerm_to_Cui(mshterm=MSHTerm)
        cui = MSHTerm_to_Cui["ui"]

        map_output["cui"] = cui


        # ---------------------------3------------------------------
        cui_to_definition = self.cui_to_definition(cui=cui)
        definition = cui_to_definition["value"]
        definition_source = cui_to_definition["rootSource"]

        map_output["definition"] = definition
        map_output["definition_source"] = definition_source


        # ---------------------------4------------------------------
        term_types = self.cui_to_termType(cui=cui)
        map_output["termType"] = term_types


        # ---------------------------5------------------------------
        synonyms = self.cui_to_synonyms(cui=cui)
        map_output["synonyms"] = synonyms

        
        # ---------------------------6------------------------------
        relations = self.cui_to_relations(cui=cui)
        map_output["relations"] = relations

        return map_output
    
    # modules
    def bc5cdrMesh_to_MSHTerm(self, mesh, bc5cdr_term=None):
        """
        1-This method gets mesh-id from bc5cdr and maps it to the term in the MSH source.

        returns:
        {
            "pageSize": 25,
            "pageNumber": 1,
            "pageCount": 1,
            "result": {
                "classType": "SourceAtomCluster",
                "ui": "D015738",
                "suppressible": false,
                "obsolete": false,
                "rootSource": "MSH",
                "atomCount": 10,
                "cVMemberCount": 0,
                "attributes": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D015738/attributes",
                "atoms": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D015738/atoms",
                "ancestors": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D015738/ancestors",
                "parents": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D015738/parents",
                "children": "NONE",
                "descendants": "NONE",
                "relations": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D015738/relations",
                "definitions": "NONE",
                "concepts": "https://uts-ws.nlm.nih.gov/rest/search/2025AA?string=D015738&sabs=MSH&searchType=exact&inputType=sourceUi",
                "defaultPreferredAtom": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D015738/atoms/preferred",
                "name": "Famotidine"
            }
        }
        """
        params = {
            'apiKey': self.umls_apikey
        }
        url = f"https://uts-ws.nlm.nih.gov/rest/content/current/source/MSH/{mesh}"
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            mesh_id = self.bc5cdrTerm_to_MSHMesh(bc5cdr_term)
            if not mesh_id is None:
                # print(self.bc5cdrMesh_to_MSHTerm(mesh=mesh_id))
                return self.bc5cdrMesh_to_MSHTerm(mesh=mesh_id)
            else:
                return
        content = response.json()
        return content['result']
    def bc5cdrTerm_to_MSHMesh(self, bc5cdr_term):
        """
        Sometimes bc5cdr mesh id is not correct in BC5CDR dataset, this class-method finds the correct mesh id from UMLS.

        response:
        {
            "pageSize": 25,
            "pageNumber": 1,
            "result": {
                "classType": "searchResults",
                "results": [
                    {
                        "ui": "D000077144",
                        "rootSource": "MSH",
                        "uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MSH/D000077144",
                        "name": "Clopidogrel"
                    }
                ],
                "recCount": 1
            }
        }
        """
        params = {
            'apiKey': self.umls_apikey,
            'string': bc5cdr_term, 
            'returnIdType': 'sourceDescriptor',
            'searchType': 'exact',
            'sabs': 'MSH'
        }
        url = "https://uts-ws.nlm.nih.gov/rest/search/current"
        response = requests.get(url=url, params=params)
        content = response.json()
        if content['result']['results']:
            return content['result']['results'][0]['ui']
        else:
            return None
    def MSHTerm_to_Cui(self, mshterm):
        """
        2- (NEED TO CALL bc5cdrMesh_to_MSHTerm) This methods map MSH term (output of bc5cdrMesh_to_MSHTerm method) to UMLS CUI.
        
        response:
        {
            "pageSize": 1,
            "pageNumber": 1,
            "result": {
                "classType": "searchResults",
                "results": [
                    {
                        "ui": "C0015620",
                        "rootSource": "MTH",
                        "uri": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0015620",
                        "name": "famotidine"
                    }
                ],
                "recCount": 1
            }
        }
        """


        params = {
            'apiKey': self.umls_apikey, 
            'string': mshterm,
            'returnIdType': 'concept',
            'searchType': 'exact',
            'pageSize': '1'
        }
        url = 'https://uts-ws.nlm.nih.gov/rest/search/current'
        response = requests.get(url=url, params=params)
        content = response.json()
        return content['result']['results'][0]
    def cui_to_definition(self, cui):
        """
        [bc5cdrMesh_to_MSHTerm --> MSHTerm_to_Cui --> cui_to_definition]
        3- This methods retrieve definition based on CUI.
        
        response:
        {
            "pageSize": 1,
            "pageNumber": 1,
            "pageCount": 6,
            "result": [
                {
                    "rootSource": "PDQ",
                    "value": "A propanimidamide and histamine H2-receptor antagonist with antacid activity. As a competitive inhibitor of histamine H2-receptors located on the basolateral membrane of the parietal cell, famotidine reduces basal and nocturnal gastric acid secretion, resulting in a reduction in gastric volume, acidity, and amount of gastric acid released in response to various stimuli. Check for \"https://www.cancer.gov/about-cancer/treatment/clinical-trials/intervention/C29045\" active clinical trials using this agent. (\"http://ncit.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI%20Thesaurus&code=C29045\" NCI Thesaurus)",
                    "classType": "Definition",
                    "sourceOriginated": true
                }
            ]
        }
        """
        source_abbreviations = [
            "AIR", "CST", "DXP", "LCH", "MCM", "ICPC", "QMR", "AOD", "RAM",
            "NCISEER", "MTHMST", "COSTAR", "UWDA", "SPN", "CCS", "HL7V2.5",
            "CSP", "AOT", "CHV", "LCH_NW", "ICD9CM", "MTHICD9", "PDQ", "FMA",
            "SOP", "CDCREC", "USPMG", "HGNC", "GO", "ICD10PCS", "NCBI", "NCI",
            "MEDLINEPLUS", "HL7V3.0", "CCSR_ICD10PCS", "CCSR_ICD10CM", "HPO",
            "MSH", "OMIM", "MVX", "CVX", "MTHCMSFRF", "DRUGBANK", "USP", "RXNORM",
            "VANDF", "MTHSPL", "ATC", "LNC", "HCPCS", "MED-RT", "MTH", "SRC",
            "JABL", "OMS", "CCC", "UMD", "ORPHANET", "MMSL", "WHO", "BI", "CPM",
            "ULT", "ICD10", "RCD", "PPAC", "RCDAE", "RCDSA", "RCDSY", "ICD10AE",
            "CCPSS", "ICD10AM", "ICD10AMAE", "DDB", "HLREL", "PCDS", "ICPC2EENG",
            "MTHICPC2EAE", "PSY", "MTHICPC2ICD10AE", "ICPC2ICD10ENG", "ICPC2P",
            "ALT", "DSM-5", "NANDA-I", "CDT", "HCDT", "ICNP", "NEU", "NIC", "NOC",
            "MDR", "CPT", "MEDCIN", "NUCCHCPT", "PNDS", "MMX", "NDDF", "GS",
            "HCPT", "ICF", "ICF-CY", "ICD10CM", "SNM", "SNMI", "SNOMEDCT_VET",
            "SNOMEDCT_US"
            ]

        params = {
            'apiKey': self.umls_apikey
        }
        url = f"https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui}/definitions"
        response = requests.get(url=url, params=params)
        content = response.json()
        try:
            for result in content["result"]:
                if result["rootSource"] in source_abbreviations:
                    return result
        except:
            None_result = {
                "rootSource": None,
                "value": None,
                "classType": "Definition",
                "sourceOriginated": None
                }
            return None_result
    def cui_to_termType(self, cui):
        """
        [bc5cdrMesh_to_MSHTerm --> MSHTerm_to_Cui --> cui_to_termType]
        4- This methods retrieve termType based on CUI.

        response:
        {
            "pageSize": 25,
            "pageNumber": 1,
            "pageCount": 1,
            "result": {
                "ui": "C0015620",
                "name": "famotidine",
                "dateAdded": "09-30-1990",
                "majorRevisionDate": "04-29-2021",
                "classType": "Concept",
                "suppressible": false,
                "status": "R",
                "semanticTypes": [
                    {
                        "name": "Organic Chemical",
                        "uri": "https://uts-ws.nlm.nih.gov/rest/semantic-network/2025AA/TUI/T109"
                    },
                    {
                        "name": "Pharmacologic Substance",
                        "uri": "https://uts-ws.nlm.nih.gov/rest/semantic-network/2025AA/TUI/T121"
                    }
                ],
                "atoms": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0015620/atoms",
                "definitions": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0015620/definitions",
                "relations": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0015620/relations",
                "defaultPreferredAtom": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0015620/atoms/preferred",
                "atomCount": 88,
                "cvMemberCount": 0,
                "attributeCount": 0,
                "relationCount": 14
            }
        }
        """
        params = {
            'apiKey': self.umls_apikey
        }
        url = f"https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui}"
        response = requests.get(url=url, params=params)
        content = response.json()
        
        termTypes = []
        for semanticType in content["result"]["semanticTypes"]:
            semanticType_name = semanticType['name']
            termTypes.append(semanticType_name)

        return termTypes
    def cui_to_synonyms(self, cui):
        """
        [bc5cdrMesh_to_MSHTerm --> MSHTerm_to_Cui --> cui_to_synonyms]
        5- This methods retrieve synonyms based on CUI.

        response: 
        {
            "pageSize": 2,
            "pageNumber": 1,
            "pageCount": 19,
            "result": [
                {
                    "classType": "Atom",
                    "ui": "A18669689",
                    "sourceDescriptor": "NONE",
                    "sourceConcept": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/CHV/0000015502",
                    "concept": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0085217",
                    "suppressible": "false",
                    "obsolete": "false",
                    "rootSource": "CHV",
                    "termType": "PT",
                    "code": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/CHV/0000015502",
                    "language": "ENG",
                    "name": "lithium carbonate",
                    "ancestors": "NONE",
                    "descendants": "NONE",
                    "attributes": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A18669689/attributes",
                    "relations": "NONE",
                    "children": "NONE",
                    "parents": "NONE"
                },
                {
                    "classType": "Atom",
                    "ui": "A13031134",
                    "sourceDescriptor": "NONE",
                    "sourceConcept": "NONE",
                    "concept": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/CUI/C0085217",
                    "suppressible": "false",
                    "obsolete": "false",
                    "rootSource": "MTHSPL",
                    "termType": "SU",
                    "code": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/source/MTHSPL/2BMD2GNA4V",
                    "language": "ENG",
                    "name": "Lithium Carbonate",
                    "ancestors": "NONE",
                    "descendants": "NONE",
                    "attributes": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A13031134/attributes",
                    "relations": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A13031134/relations",
                    "children": "NONE",
                    "parents": "NONE"
                }
            ]
        }
        """
        params = {
                    'apiKey': self.umls_apikey,
                    'language': 'ENG',
                    'pageSize':40
                }
        url = f"https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui}/atoms"
        response = requests.get(url=url, params=params)
        content = response.json()

        synonyms = set()
        for result in content['result']:
            synonyms.add(result['name'].lower())
        return list(synonyms)
    def cui_to_relations(self, cui):
        """
        [bc5cdrMesh_to_MSHTerm --> MSHTerm_to_Cui --> cui_to_synonyms]
        6- This method retrieve relations based on CUI.

        response:
        {
            "pageSize": 100,
            "pageNumber": 1,
            "pageCount": 1,
            "result": [
                {
                    "ui": "R04234789",
                    "suppressible": false,
                    "sourceUi": "NONE",
                    "obsolete": false,
                    "sourceOriginated": false,
                    "rootSource": "SNMI",
                    "groupId": "NONE",
                    "attributeCount": 0,
                    "classType": "AtomRelation",
                    "relatedFromId": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A0542922",
                    "relatedFromIdName": "Closed fracture of wrist, NOS",
                    "relationLabel": "RO",
                    "additionalRelationLabel": "associated_with",
                    "relatedId": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A0704559",
                    "relatedIdName": "Fracture, closed, NOS"
                },
                {
                    "ui": "R04234600",
                    "suppressible": false,
                    "sourceUi": "NONE",
                    "obsolete": false,
                    "sourceOriginated": false,
                    "rootSource": "SNMI",
                    "groupId": "NONE",
                    "attributeCount": 0,
                    "classType": "AtomRelation",
                    "relatedFromId": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A0542680",
                    "relatedFromIdName": "Closed fracture carpal bone, NOS",
                    "relationLabel": "RO",
                    "additionalRelationLabel": "associated_with",
                    "relatedId": "https://uts-ws.nlm.nih.gov/rest/content/2025AA/AUI/A0704559",
                    "relatedIdName": "Fracture, closed, NOS"
                }
            ]
        }
        """

        RELAs = ['may_treat', 'may_prevent', 'may_diagnose', 'induces', 'contraindicated_with_disease', 
                 'has_mechanism_of_action', 'has_physiological_effect', 'causes', 'is_treated_by', 'is_prevented_by',
                 'is_diagnosed_by', 'adverse_effect_of', 'associated_with', 'has_side_effect', 'contraindicates', 
                 'biological_process_involves_chemical_or_drug', 'chemical_or_drug_involves_biological_process',
                 'metabolized_to', 'has_active_metabolite', 'has_precise_ingredient']
        RELAs_string = ','.join(RELAs)

        SABs = ['MED-RT', 'NDFRT', 'RXNORM', 'DRUGBANK', 'ATC', 'GS', 'VANDF', 'MTHSPL', 'USP', 'MMSL']
        SABs_string = ','.join(SABs)

        params = {
                    'apiKey': self.umls_apikey,
                    'includeAdditionalRelationLabels': RELAs_string,
                    'sabs': SABs_string,
                    'pageSize': 100
                }
        url = f"https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui}/relations"
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            return []
        content = response.json()


        relations = []
        RELA_abbr_to_desc = FilesUtils.read_json(path="Abbreviations\\Relationship_Attribute.json")
        for result in content['result']:
            one_relation ={
                "relation": RELA_abbr_to_desc[result['additionalRelationLabel']],
                "entity_1_name": result['relatedFromIdName'],
                "entity_1_uri": result['relatedFromId'],
                "entity_2_name": result['relatedIdName'],
                "entity_2_uri": result['relatedId']
            }
            relations.append(one_relation)
        return relations
#  -----------------Retrieve Term information------------------


if __name__ == "__main__":
    umls = UMLS(apikey='06d145b2-e6f7-4803-9bd0-5c2a9cfb3102')
    # r = umls.map_bc5cdr_to_umls(mesh="D016651")
    # r = umls.cui_to_definition(cui="C0085217")
    # r = umls.cui_to_synonyms(cui="C0085217")
    r = umls.cui_to_relations(cui="C0085217")
    print(r)
    