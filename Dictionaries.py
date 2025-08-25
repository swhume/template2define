from odmlib.define_2_1 import model as DEFINE
import define_object

""" Note: Dictionaries have not yet been implemented in the template """
class Dictionaries(define_object.DefineObject):
    """ create a Define-XML v2.1 ExternalCodeList element template """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, objects, lang, acrf):
        """
        parse the define-template and create odmlib define_objects to return in the define_objects dictionary
        :param template: define-template dictionary section
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        for codelist in template:
            cl_oid = self.generate_oid(["CL", codelist["Short Name"]])
            cl = self._create_codelist_object(cl_oid, codelist)
            objects["CodeList"].append(cl)

    def _create_codelist_object(self, cl_oid, codelist):
        """
        using the row from the Dictionaries worksheet create an odmlib CodeList template and add ExternalCodeList
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
