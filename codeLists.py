from odmlib.define_2_1 import model as DEFINE
import define_object


class CodeLists(define_object.DefineObject):
    """ create a Define-XML v2.1 CodeList element template """
    def __init__(self):
        super().__init__()
        self.igd = None

    def create_define_objects(self, object, define_objects, lang, acrf):
        """
        parse the define-template dictionary and create odmlib define_objects to return in the define_objects dictionary
        :param object: code list section of the DDS template metadata
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        define_objects["CodeList"] = []
        for cl in object:
            # TODO template missing the NCI c-codes for codelists and terms
            cl_defn = self._create_codelist_object(cl)
            cl_c_code = cl.get("nciCodelistCode")
            for term in cl["codeListItems"]:
                cl_item = self._create_codelistitem_object(term)
                cl_defn.CodeListItem.append(cl_item)
            # TODO no indicator that a codelist is a dictionary with an external codelist reference
            if len(cl["codeListItems"]) == 0:
                self._create_external_code_list(cl_defn, cl)
            self._add_codelist_to_objects(cl_c_code, cl_defn, define_objects)

    @staticmethod
    def _create_external_code_list(cl, obj):
        # TODO temp to create the external codelist content
        attr = {"Dictionary": obj["name"], "Version": "1.0", "href": "https://www.iso.org"}
        exd = DEFINE.ExternalCodeList(**attr)
        cl.ExternalCodeList = exd

    @staticmethod
    def _add_codelist_to_objects(cl_c_code, cl, objects):
        if cl_c_code:
            alias = DEFINE.Alias(Context="nci:ExtCodeID", Name=cl_c_code)
            cl.Alias.append(alias)
        # add the code list to the list of code list define_objects
        if cl:
            objects["CodeList"].append(cl)

    @staticmethod
    def _create_codelist_object(obj):
        data_type = obj.get("dataType", "text")
        attr = {"OID": obj["OID"], "Name": obj["name"], "DataType": data_type}
        if obj.get("comment"):
            attr["CommentOID"] = obj["comment"]
        if obj.get("isNonStandard"):
            attr["IsNonStandard"] = obj["isNonStandard"]
        if obj.get("standardOID"):
            attr["StandardOID"] = obj["standardOID"]
        cl = DEFINE.CodeList(**attr)
        return cl

    @staticmethod
    def _create_enumerateditem_object(obj):
        attr = {"CodedValue": obj["Term"]}
        if obj.get("Order"):
            attr["OrderNumber"] = obj["Order"]
        en_item = DEFINE.EnumeratedItem(**attr)
        if obj.get("NCI Term Code"):
            alias = DEFINE.Alias(Context="nci:ExtCodeID", Name=obj["NCI Term Code"])
            en_item.Alias.append(alias)
        return en_item

    @staticmethod
    def _create_codelistitem_object(obj):
        attr = {"CodedValue": obj["codedValue"]}
        if obj.get("order"):
            attr["OrderNumber"] = obj["order"]
        cl_item = DEFINE.CodeListItem(**attr)
        decode = DEFINE.Decode()
        if obj.get("decode", None):
            tt = DEFINE.TranslatedText(_content=obj["decode"], lang="en")
        else:
            # assumption: if no decode for this term the use the submission value
            tt = DEFINE.TranslatedText(_content=obj["codedValue"], lang="en")
        decode.TranslatedText.append(tt)
        cl_item.Decode = decode
        # TODO NCI c-codes for terms or codelists not available in template
        if obj.get("nciTermCode"):
            alias = DEFINE.Alias(Context="nci:ExtCodeID", Name=obj["nciTermCode"])
            cl_item.Alias.append(alias)
        return cl_item
