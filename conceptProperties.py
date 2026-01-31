from odmlib.define_2_1 import model as DEFINE
import define_object

class ConceptProperties(define_object.DefineObject):
    """ create a Define-XML v2.1 ExternalCodeList element template """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, objects, lang, acrf):
        """
        parse the define-template and create odmlib define_objects to return in the define_objects dictionary
        :param template: DDS template dictionary section
        :param objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        for concept in template:
            cl_oid = self.generate_oid(["CL", concept["Short Name"]])
            cl = self._create_concept_object(cl_oid, concept)
            objects["CodeList"].append(cl)

    @staticmethod
    def _create_concept_object(cl_oid, codelist):
        """
        using the row from the Dictionaries worksheet create an odmlib CodeList template and add ExternalCodeList
        :param cl_oid: codelist OID
        :param codelist: dictionary with contents the Dictionaries template section
        :return: CodeList odmlib template with ExternalCodeList
        """
        cl = DEFINE.CodeList(OID=cl_oid, Name=codelist["Name"], DataType=codelist["Data Type"])
        attr = {"Dictionary": codelist["Dictionary"]}
        if codelist.get("Version"):
            attr["Version"] = codelist["Version"]
        exd = DEFINE.ExternalCodeList(**attr)
        cl.ExternalCodeList = exd
        return cl
