from odmlib.define_2_1 import model as DEFINE
import define_object
# import ValueLevel as VL


class ItemRefs(define_object.DefineObject):
    """ create a Define-XML v2.1 ItemRef element objects """
    def __init__(self):
        super().__init__()
        self.lookup_oid = None
        self.igd = None
        self.item_def_oids = []
        self.vlm_oids = []

    def create_define_objects(self, template, define_objects, lang, acrf, item_group=None):
        self.lang = lang
        self.acrf = acrf
        item_oids = []
        # vl = VL.ValueLevel()
        for variable in template:
            it_oid = variable["itemOID"]
            self._create_itemref_object(variable, define_objects, item_group, it_oid)

    def _create_itemref_object(self, obj, define_objects, igd, it_oid):
        # if dataset_oid != self.lookup_oid:
        #     self.lookup_oid = dataset_oid
        #     self.igd = self.find_object(define_objects["ItemGroupDef"], self.lookup_oid)
        # if self.igd is None:
        #     raise ValueError(f"ItemGroupDef with OID {dataset_oid} is missing from the Datasets tab")
        if "mandatory" not in obj:
            mandatory = "No"
        else:
            mandatory = obj["mandatory"]
        attr = {"ItemOID": it_oid, "Mandatory": mandatory}
        self._add_optional_itemref_attributes(attr, obj)
        item = DEFINE.ItemRef(**attr)
        igd.ItemRef.append(item)

    def _add_optional_itemref_attributes(self, attr, obj):
        """
        use the values from the Variables worksheet row to add the optional attributes to the attr dictionary
        :param attr: ItemRef template attributes to update with optional values
        :param row: Variables worksheet row values as a dictionary
        """
        if obj.get("method"):
            attr["MethodOID"] = obj["method"]
        # TODO consider generating OrderNumber if not provided
        if obj.get("order"):
            attr["OrderNumber"] = int(obj["order"])
        if obj.get("keySequence"):
            attr["KeySequence"] = int(obj["keySequence"])
        if obj.get("mandatory"):
            attr["Mandatory"] = obj["mandatory"]
        else:
            attr["Mandatory"] = "No"
        if obj.get("role"):
            attr["Role"] = obj["role"]
        if obj.get("isNonStandard"):
            attr["IsNonStandard"] = obj["isNonStandard"]
        if obj.get("hasNoData"):
            attr["HasNoData"] = obj["hasNoData"]

    # def _create_itemdef_object(self, obj, oid):
    #     attr = {"OID": oid, "Name": obj["name"], "DataType": obj["dataType"], "SASFieldName": obj["name"]}
    #     self._add_optional_itemdef_attributes(attr, obj)
    #     item = DEFINE.ItemDef(**attr)
    #     tt = DEFINE.TranslatedText(_content=obj["description"], lang=self.lang)
    #     item.Description = DEFINE.Description()
    #     item.Description.TranslatedText.append(tt)
    #     # self._add_optional_itemdef_elements(item, obj, oid, vl_oid)
    #     self._add_optional_itemdef_elements(item, obj, oid)
    #     return item

    # def _add_optional_itemdef_elements(self, item, obj, it_oid):
    #     """
    #     use the values from the Variables section in the define-template to add the optional ELEMENTS to the ItemDef
    #     """
    #     # TODO do not find codeList in define.json example for items (nice to have that reference)
    #     if obj.get("codeList"):
    #         cl_oid = self.generate_oid(["CL", obj["codeList"][0]])
    #         cl = DEFINE.CodeListRef(CodeListOID=cl_oid)
    #         item.CodeListRef = cl
    #     # TODO do not find origin content in define.json example for items (nice to have that information)
    #     if obj.get("originType"):
    #         # define-template input only provides for 1 Origin, but multiple are supported by the spec
    #         attr = {"Type": obj["Origin Type"]}
    #         if obj.get("Origin Source"):
    #             attr["Source"] = obj["Origin Source"]
    #         item.Origin.append(DEFINE.Origin(**attr))
    #         if obj.get("predecessor"):
    #             item.Origin[0].Description = DEFINE.Description()
    #             item.Origin[0].Description.TranslatedText.append(DEFINE.TranslatedText(_content=obj["Predecessor"]))
    #         if obj.get("pages"):
    #             dr = DEFINE.DocumentRef(leafID=self.acrf)
    #             dr.PDFPageRef.append(DEFINE.PDFPageRef(PageRefs=obj["Pages"], Type="PhysicalRef"))
    #             item.Origin[0].DocumentRef.append(dr)
    #     # TODO do not find VLM reference in define.json example for items (nice to have that information)
    #     # if obj.get("VLM"):
    #     #     vl = DEFINE.ValueListRef(ValueListOID=vl_oid)
    #     #     item.ValueListRef = vl
    #
    # def _add_optional_itemdef_attributes(self, attr, obj):
    #     """
    #     use the values from the Variables section in the define-template to add the optional attributes to the ItemDef
    #     """
    #     if obj.get("length"):
    #         attr["Length"] = obj["length"]
    #     if obj.get("significantDigits"):
    #         attr["SignificantDigits"] = obj["significantDigits"]
    #     # TODO do not find format content in define.json example for items
    #     if obj.get("format"):
    #         attr["DisplayFormat"] = obj["format"]
    #     if obj.get("comment"):
    #         attr["CommentOID"] = obj["comment"]
