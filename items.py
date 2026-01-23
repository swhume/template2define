from odmlib.define_2_1 import model as DEFINE
import define_object
# import ValueLevel as VL


class Items(define_object.DefineObject):
    """ create a Define-XML v2.1 ItemDef element objects """
    def __init__(self):
        super().__init__()
        self.lookup_oid = None
        self.igd = None
        self.item_def_oids = []
        self.vlm_oids = []

    def create_define_objects(self, template, define_objects, lang, acrf, item_group=None):
        self.lang = lang
        self.acrf = acrf
        define_objects["ItemDef"] = []
        for variable in template:
            it_oid = variable["OID"]
            item = self._create_itemdef_object(variable, it_oid)
            define_objects["ItemDef"].append(item)
        self._create_leaf_objects(define_objects)

    def _create_itemdef_object(self, obj,  oid):
        attr = {"OID": oid, "Name": obj["name"], "DataType": obj["dataType"], "SASFieldName": obj["name"]}
        self._add_optional_itemdef_attributes(attr, obj)
        item = DEFINE.ItemDef(**attr)
        if obj.get("description"):
            tt = DEFINE.TranslatedText(_content=obj["description"], lang=self.lang)
            item.Description = DEFINE.Description()
            item.Description.TranslatedText.append(tt)
        self._add_optional_itemdef_elements(item, obj, oid)
        return item

    def _add_optional_itemdef_elements(self, item, obj, it_oid):
        """
        use the values from the Variables section in the define-template to add the optional ELEMENTS to the ItemDef
        """
        # TODO do not find codeList in define.json example for items
        if obj.get("codeList"):
            cl_oid = self.generate_oid(["CL", obj["codeList"][0]])
            cl = DEFINE.CodeListRef(CodeListOID=cl_oid)
            item.CodeListRef = cl
        # TODO do not find origin content in define.json example for items (nice to have that information)
        attr = {}
        if obj.get("origin"):
            # define-template input only provides for 1 Origin, but multiple are supported by the spec
            if obj.get("origin").get("type"):
                attr["Type"] =  obj["origin"]["type"]
            if obj.get("origin").get("source"):
                attr["Source"] = obj["origin"]["source"]
            item.Origin.append(DEFINE.Origin(**attr))
            if obj.get("predecessor"):
                item.Origin[0].Description = DEFINE.Description()
                item.Origin[0].Description.TranslatedText.append(DEFINE.TranslatedText(_content=obj["Predecessor"]))
            if obj.get("pages"):
                dr = DEFINE.DocumentRef(leafID=self.acrf)
                dr.PDFPageRef.append(DEFINE.PDFPageRef(PageRefs=obj["Pages"], Type="PhysicalRef"))
                item.Origin[0].DocumentRef.append(dr)
        # TODO do not find VLM reference in define.json example for items (nice to have that information)
        # if obj.get("VLM"):
        #     vl = DEFINE.ValueListRef(ValueListOID=vl_oid)
        #     item.ValueListRef = vl

    def _add_optional_itemdef_attributes(self, attr, obj):
        """
        use the values from the Variables section in the define-template to add the optional attributes to the ItemDef
        """
        if obj.get("length"):
            attr["Length"] = obj["length"]
        if obj.get("significantDigits"):
            attr["SignificantDigits"] = obj["significantDigits"]
        # TODO do not find format content in define.json example for items
        if obj.get("format"):
            attr["DisplayFormat"] = obj["format"]
        if obj.get("comment"):
            attr["CommentOID"] = obj["comment"]

    def _create_leaf_objects(self, define_objects):
        """
        each ItemGroupDef template in define_objects is updated to add a leaf template
        :param define_objects: dictionary of odmlib define_objects updated by this method
        """
        # TODO temp
        # for igd in define_objects["ItemGroupDef"]:
        #     # move Class to the end of the OrderedDict before adding leaf
        #     igd_class = igd.__dict__.pop("Class")
        #     igd.Class = igd_class
        #     id = self.generate_oid(["LF", igd.Name])
        #     xpt_name = igd.Name + ".xpt"
        #     leaf = DEFINE.leaf(ID=id, href=xpt_name.lower())
        #     title = DEFINE.title(_content=xpt_name.lower())
        #     leaf.title = title
        #     igd.leaf = leaf
        pass

