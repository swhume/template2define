import argparse
import json
import logging
from pathlib import Path
import odm as ODM
import supporting_docs as SD
import os.path
from validate import DefineSchemaValidator, DefineSchemaValidationError
import study, standards, itemGroups, itemRefs, items, conditions, standards, annotatedCRF, concepts, conceptProperties
import whereClauses, codeLists, Dictionaries, methods, Comments, Documents, valueLevel

ELEMENTS = ["ValueListDef", "WhereClauseDef", "ItemGroupDef", "ItemDef", "CodeList", "MethodDef", "CommentDef", "leaf"]

"""
define_generator.py - convert a define-360i-2026-01-01.json file into a Define-XML v2.1 file.
Example Cmd-line Args:
    example: -t ./data/define-360i.json -d ./data/define-360i.xml

Example CLI validation:
xmllint --schema /home/sam/src/schemas/DefineV219/schema/cdisc-define-2.1/define2-1-0.xsd ./data/define-360i.xml --noout

Example XML Pretty Print:
xmllint --format ./data/define-360i.xml | less
"""

# TODO template comments
# "asOfDateTime": null - should exclude attributes with null values
# need a valuelist attribute on items with associated ValueListDefs so I can assign the ValueListRef
# need a wasDerivedFrom attribute on a codelist like we have on an itemGroup so I can assign the CT standard used
"""
logging.debug("Debug message: for troubleshooting and deep info")
logging.info("Info message: normal operation information")
logging.warning("Warning message: something looks off")
logging.error("Error message: an issue occurred")
logging.critical("Critical message: major failure")
"""


class DefineGenerator:
    """ Generate a Define-XML v2.1 file from the DDS JSON file. """
    def __init__(self, dds_file, define_file, log_level="INFO"):
        """
        :param dds_file: str - the Data Definition Specification (DDS) path and filename
        :param define_file: str - the Define-XML v2.1 path and filename
        :param log_level: str - sets the logging level
        """
        self.dds_file = dds_file
        self.define_file = define_file
        logging.basicConfig(
            filename="define_generator.log",
            level=getattr(logging, log_level),
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self._check_file_existence()
        self.lang = "en"
        self.acrf = "LF.acrf"
        self.define_attributes = {}
        self.define_objects = {}

    def create(self):
        """
        public method to create the Define-XML v2.1 file from the template input file
        """
        with open(self.dds_file, 'r') as f:
            template_objects = json.load(f)
        self._init_define_objects()
        self._load_study(template_objects)
        for section, object in template_objects.items():
            if type(object) is list:
                logging.info(f"processing {section}")
                self._load(section, object)
            else:
                self.define_attributes[section] = object

        odm = self._build_doc()
        self._write_define(odm)

    def _init_define_objects(self):
        for elem in ELEMENTS:
            self.define_objects[elem] = []

    def _load(self, section, object):
        loader = eval(section + "." + section[0].upper() + section[1:] + "()")
        loader.create_define_objects(object, self.define_objects, self.lang, self.acrf)

    def _load_study(self, template):
        loader = study.Study()
        loader.create_define_objects(template, self.define_objects, self.lang, self.acrf)

    def _build_doc(self):
        """
        after processing the content in the template input file organize the odmlib define_objects for use as a Define-XML v2.1
        :return: instantiated odmlib Define-XML v2.1 model
        """
        odm_elem = ODM.ODM()
        odm = odm_elem.create_define_objects()
        odm.Study = self.define_objects["Study"]
        odm.Study.MetaDataVersion = self.define_objects["MetaDataVersion"]
        odm.Study.MetaDataVersion.Standards = self.define_objects["Standards"]
        supp_docs = SD.SupportingDocuments()
        odm.Study.MetaDataVersion.AnnotatedCRF = supp_docs.create_annotatedcrf(self.acrf)
        # create leaf object for aCRF as there are no documents in template
        self.define_objects["leaf"].append(supp_docs.create_leaf_object(leaf_id="LF.acrf", href="acrf.pdf", title="Annotated CRF"))
        # TODO no supplemental docs in template
        # if "leaf" in self.define_objects and len(self.define_objects["leaf"]) > 0:
        #     odm.Study.MetaDataVersion.SupplementalDoc = supp_docs.create_supplementaldoc(self.acrf, self.define_objects["leaf"])
        for elem in ELEMENTS:
            self._load_elements(odm, elem)
        return odm


    def _load_elements(self, odm, elem_name):
        """
        when building the doc, add the instantiated define_objects to the odmlib MetaDataVersion
        :param odm: odmlib Define-XML define_objects created to represent Define-XML v2.0
        :param elem_name: name of the element define_objects to add to MetaDataVersion
        """
        for obj in self.define_objects[elem_name]:
            eval("odm.Study.MetaDataVersion." + elem_name + ".append(obj)")

    def _write_define(self, odm):
        """
        write the odmlib Define-XML out as an XML file
        :param odm: the instantiated odmlib Define-XML
        """
        odm.write_xml(self.define_file)

    def _check_file_existence(self):
        """ throw an error if the Excel input file cannot be found """
        if not os.path.isfile(self.dds_file):
            raise ValueError("The template file specified on the command-line cannot be found.")

def validate_defile_file(define_file):
    validator = DefineSchemaValidator(Path(define_file))
    try:
        validator.validate_define_file()
    except DefineSchemaValidationError as e:
        logging.info(f"Define-XML schema validation errors: {e}")
    else:
        logging.info("Define-XML file is valid.")

def set_cmd_line_args():
    """
    get the command-line arguments needed to convert the define-template.json input file into Define-XML 2.1 file
    :return: return the argparse template with the command-line parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--define", help="path and file name of Define-XML v2 file to create", required=False,
                        dest="define_file", default="./data/define-360i.xml")
    parser.add_argument("-t", "--template", help="path and file name of the template file to load", required=True,
                        dest="dds_file", )
    parser.add_argument("-l", "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument("-s", "--validate", help="schema validate the define.xml", default=False, const=True,
                        nargs='?', dest="is_validate")
    args = parser.parse_args()
    return args


def main():
    """ The main driver method that generates Define-XML v2.1 file from the DDS template metadata file """
    args = set_cmd_line_args()
    dg = DefineGenerator(dds_file=args.dds_file, define_file=args.define_file, log_level=args.log_level)
    dg.create()
    if args.is_validate:
        validate_defile_file(args.define_file)


if __name__ == "__main__":
    main()
