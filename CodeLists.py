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
        :param object: code list section of the define-template metadata
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        define_objects["CodeList"] = []
        is_decode_item = False
        cl_oids = []
        for codelist in object:
            for cl in codelist["CodeList"]:
                oid = self.generate_oid(["CL", cl["Short Name"]])
                if oid not in cl_oids:
                    # assumes when this is a new code list the names will not be the same
                    cl_defn = self._create_codelist_object(cl)
                    cl_c_code = cl.get("NCI Codelist Code")
                    is_first_term = True
                    for term in cl["Terms"]:
                        # assumption: if the first term has a decode element then create the list with decodes
                        if is_first_term:
                            if term["Decoded Value"]:
                                is_decode_item = True
                            else:
                                is_decode_item = False
                            is_first_term = False
                        if is_decode_item:
                            cl_item = self._create_codelistitem_object(term)
                            cl_defn.CodeListItem.append(cl_item)
                        else:
                            en_item = self._create_enumerateditem_object(term)
                            cl_defn.EnumeratedItem.append(en_item)
                        cl_oids.append(oid)
                    self._add_previous_codelist_to_objects(cl_c_code, cl_defn, define_objects)

    def _add_previous_codelist_to_objects(self, cl_c_code, cl, objects):
        if cl_c_code:
            alias = DEFINE.Alias(Context="nci:ExtCodeID", Name=cl_c_code)
            cl.Alias.append(alias)
        # add the code list to the list of code list define_objects
        if cl:
            objects["CodeList"].append(cl)

    def _create_codelist_object(self, obj):
        oid = self.generate_oid(["CL", obj["Short Name"]])
        data_type = "text"
        attr = {"OID": oid, "Name": obj["Name"], "DataType": data_type}
        if obj.get("Comment"):
            attr["CommentOID"] = obj["Comment"]
        if obj.get("IsNonStandard"):
            attr["IsNonStandard"] = obj["IsNonStandard"]
        if obj.get("StandardOID"):
            attr["StandardOID"] = obj["StandardOID"]
        cl = DEFINE.CodeList(**attr)
        return cl

    def _create_enumerateditem_object(self, obj):
        attr = {"CodedValue": obj["Term"]}
        if obj.get("Order"):
            attr["OrderNumber"] = obj["Order"]
        en_item = DEFINE.EnumeratedItem(**attr)
        if obj.get("NCI Term Code"):
            alias = DEFINE.Alias(Context="nci:ExtCodeID", Name=obj["NCI Term Code"])
            en_item.Alias.append(alias)
        return en_item

    def _create_codelistitem_object(self, obj):
        attr = {"CodedValue": obj["Term"]}
        if obj.get("Order"):
            attr["OrderNumber"] = obj["Order"]
        cl_item = DEFINE.CodeListItem(**attr)
        decode = DEFINE.Decode()
        if obj["Decoded Value"]:
            # assumption: decoded value is a list in the template, but just need one value
            tt = DEFINE.TranslatedText(_content=obj["Decoded Value"][0], lang="en")
        else:
            # assumption: if no decode for this term the use the submission value
            tt = DEFINE.TranslatedText(_content=obj["Term"], lang="en")
        decode.TranslatedText.append(tt)
        cl_item.Decode = decode
        if obj.get("NCI Term Code"):
            alias = DEFINE.Alias(Context="nci:ExtCodeID", Name=obj["NCI Term Code"])
            cl_item.Alias.append(alias)
        return cl_item
