import argparse
import odm as ODM
import supporting_docs as SD
import os.path
import Study, Standards, Datasets, Variables, ValueLevel
import WhereClauses, CodeLists, Dictionaries, Methods, Comments, Documents

ELEMENTS = ["ValueListDef", "WhereClauseDef", "ItemGroupDef", "ItemDef", "CodeList", "MethodDef", "CommentDef", "leaf"]

"""
template2define2-1.py - convert a define-template.json file into a Define-XML v2.1 file.
Example Cmd-line Args:
    example: -t ./data/Define-Template.json -d ./data/define-360i.xml

Example CLI validation:
xmllint --schema /home/sam/src/schemas/DefineV219/schema/cdisc-define-2.1/define2-1-0.xsd ./data/define-360i.xml --noout
"""


class Template2Define:
    """ Generate a Define-XML v2.1 file from the define-template.json file. """
    def __init__(self, template_file, define_file, is_verbose=False):
        """
        :param template_file: str - the path and filename for the define template file
        :param define_file: str - the path and filename for the Define-XML v2.1 file to be generated
        """
        self.template_file = template_file
        self.define_file = define_file
        self.is_verbose = is_verbose
        self._check_file_existence()
        self.lang = "en"
        self.acrf = "LF.acrf"
        self.define_objects = {}

    def create(self):
        """
        public method to create the Define-XML v2.1 file from the template input file
        """
        with open(self.template_file, 'r') as f:
            template_objects = eval(f.read())
        self._init_define_objects()
        for section, object in template_objects.items():
            print(section)
            self._load(section, object)
        odm = self._build_doc()
        self._write_define(odm)

    def _init_define_objects(self):
        for elem in ELEMENTS:
            self.define_objects[elem] = []

    def _load(self, section, object):
        loader = eval(section + "." + section + "()")
        loader.create_define_objects(object, self.define_objects, self.lang, self.acrf)

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
        if "leaf" in self.define_objects and len(self.define_objects["leaf"]) > 0:
            odm.Study.MetaDataVersion.SupplementalDoc = supp_docs.create_supplementaldoc(self.acrf, self.define_objects["leaf"])
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
        if not os.path.isfile(self.template_file):
            raise ValueError("The template file specified on the command-line cannot be found.")

def set_cmd_line_args():
    """
    get the command-line arguments needed to convert the define-template.json input file into Define-XML 2.1 file
    :return: return the argparse template with the command-line parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--define", help="path and file name of Define-XML v2 file to create", required=False,
                        dest="define_file", default="./odmlib-define-xml.xml")
    parser.add_argument("-t", "--template", help="path and file name of the template file to load", required=True,
                        dest="template_file", )
    parser.add_argument("-v", "--verbose", help="turn on verbose processing", default=False, const=True,
                        nargs='?', dest="is_verbose")
    args = parser.parse_args()
    return args


def main():
    """ The main driver method that generates Define-XML v2.1 file from the define-template.json metadata file """
    args = set_cmd_line_args()
    x2d = Template2Define(template_file=args.template_file, define_file=args.define_file, is_verbose=args.is_verbose)
    x2d.create()

if __name__ == "__main__":
    main()
