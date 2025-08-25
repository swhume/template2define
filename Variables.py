from odmlib.define_2_1 import model as DEFINE
import define_object
import ValueLevel as VL


class Variables(define_object.DefineObject):
    """ create a Define-XML v2.1 ItemDef element objects """
    def __init__(self):
        super().__init__()
        self.lookup_oid = None
        self.igd = None
        self.item_def_oids = []
        self.vlm_oids = []

    def create_define_objects(self, template, define_objects, item_group, lang, acrf):
        self.lang = lang
        self.acrf = acrf
        item_oids = []
        vl = VL.ValueLevel()
        for variable in template:
            it_oid = self.generate_oid(["IT", item_group.Name, variable["Variable"]])
            vl_oid = self.generate_oid(["VL", item_group.Name, variable["Variable"]])
            if it_oid not in self.item_def_oids:
                item = self._create_itemdef_object(variable, it_oid, vl_oid)
                define_objects["ItemDef"].append(item)
                self.item_def_oids.append(it_oid)
            self._create_itemref_object(variable, define_objects, item_group.OID, it_oid)
            if "VLM" in variable:
                vl.create_define_objects(variable, define_objects, vl_oid, item_oids, self.lang, self.acrf)
        self._create_leaf_objects(define_objects)

    def _create_itemdef_object(self, obj, oid, vl_oid):
        if obj["Data Type"] == "Char":
            data_type = "text"
        else:
            data_type = "float"
        attr = {"OID": oid, "Name": obj["Variable"], "DataType": data_type, "SASFieldName": obj["Variable"]}
        self._add_optional_itemdef_attributes(attr, obj)
        item = DEFINE.ItemDef(**attr)
        tt = DEFINE.TranslatedText(_content=obj["Label"], lang=self.lang)
        item.Description = DEFINE.Description()
        item.Description.TranslatedText.append(tt)
        self._add_optional_itemdef_elements(item, obj, oid, vl_oid)
        return item

    def _add_optional_itemdef_elements(self, item, obj, it_oid, vl_oid):
        """
        use the values from the Variables section in the define-template to add the optional ELEMENTS to the ItemDef
        """
        if obj.get("CodeList"):
            cl_oid = self.generate_oid(["CL", obj["CodeList"][0]])
            cl = DEFINE.CodeListRef(CodeListOID=cl_oid)
            item.CodeListRef = cl
        if obj.get("Origin Type"):
            # define-template input only provides for 1 Origin, but multiple are supported by the spec
            attr = {"Type": obj["Origin Type"]}
            if obj.get("Origin Source"):
                attr["Source"] = obj["Origin Source"]
            item.Origin.append(DEFINE.Origin(**attr))
            if obj.get("Predecessor"):
                item.Origin[0].Description = DEFINE.Description()
                item.Origin[0].Description.TranslatedText.append(DEFINE.TranslatedText(_content=obj["Predecessor"]))
            if obj.get("Pages"):
                dr = DEFINE.DocumentRef(leafID=self.acrf)
                dr.PDFPageRef.append(DEFINE.PDFPageRef(PageRefs=obj["Pages"], Type="PhysicalRef"))
                item.Origin[0].DocumentRef.append(dr)
        if obj.get("VLM"):
            vl = DEFINE.ValueListRef(ValueListOID=vl_oid)
            item.ValueListRef = vl

    def _add_optional_itemdef_attributes(self, attr, obj):
        """
        use the values from the Variables section in the define-template to add the optional attributes to the ItemDef
        """
        if obj.get("Length"):
            attr["Length"] = obj["Length"]
        if obj.get("Significant Digits"):
            attr["SignificantDigits"] = obj["Significant Digits"]
        if obj.get("Format"):
            attr["DisplayFormat"] = obj["Format"]
        if obj.get("Comment"):
            attr["CommentOID"] = obj["Comment"]

    def _create_itemref_object(self, obj, define_objects, dataset_oid, it_oid):
        if dataset_oid != self.lookup_oid:
            self.lookup_oid = dataset_oid
            self.igd = self.find_object(define_objects["ItemGroupDef"], self.lookup_oid)
        if self.igd is None:
            raise ValueError(f"ItemGroupDef with OID {dataset_oid} is missing from the Datasets tab")
        if "Mandatory" not in obj:
            mandatory = "No"
        else:
            mandatory = obj["Mandatory"]
        attr = {"ItemOID": it_oid, "Mandatory": mandatory}
        self._add_optional_itemref_attributes(attr, obj)
        item = DEFINE.ItemRef(**attr)
        self.igd.ItemRef.append(item)

    def _add_optional_itemref_attributes(self, attr, obj):
        """
        use the values from the Variables worksheet row to add the optional attributes to the attr dictionary
        :param attr: ItemRef template attributes to update with optional values
        :param row: Variables worksheet row values as a dictionary
        """
        if obj.get("Method"):
            attr["MethodOID"] = obj["Method"]
        if obj.get("Order"):
            attr["OrderNumber"] = int(obj["Order"])
        if obj.get("KeySequence"):
            attr["KeySequence"] = int(obj["KeySequence"])
        if obj.get("Role"):
            attr["Role"] = obj["Role"]
        if obj.get("IsNonStandard"):
            attr["IsNonStandard"] = obj["IsNonStandard"]
        if obj.get("HasNoData"):
            attr["HasNoData"] = obj["HasNoData"]

    def _create_leaf_objects(self, define_objects):
        """
        each ItemGroupDef template in define_objects is updated to add a leaf template
        :param define_objects: dictionary of odmlib define_objects updated by this method
        """
        for igd in define_objects["ItemGroupDef"]:
            # move Class to the end of the OrderedDict before adding leaf
            igd_class = igd.__dict__.pop("Class")
            igd.Class = igd_class
            id = self.generate_oid(["LF", igd.Name])
            xpt_name = igd.Name + ".xpt"
            leaf = DEFINE.leaf(ID=id, href=xpt_name.lower())
            title = DEFINE.title(_content=xpt_name.lower())
            leaf.title = title
            igd.leaf = leaf
