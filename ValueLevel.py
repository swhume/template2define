from odmlib.define_2_1 import model as DEFINE
import define_object
import WhereClauses as WC


class ValueLevel(define_object.DefineObject):
    """ create a Define-XML v2.0 ValueListDef element template """
    def __init__(self):
        super().__init__()
        self.lookup_oid = None
        self.vld = None

    def create_define_objects(self, template, define_objects, oid, item_oids, lang, acrf):
        """
        parse the define-template and create a odmlib define_objects to return in the define_objects dictionary
        """
        self.lang = lang
        self.acrf = acrf
        prefix, dataset, variable = oid.split(".")
        self._create_valuelistdef_object(oid, define_objects)
        for vl in template["VLM"]:
            for order, wc in enumerate(vl["WhereClause"], 1):
                wc_variable = wc["Clause"][0]["Values"][0]
                it_oid = self.generate_oid(["IT", dataset, variable, wc_variable])
                if it_oid not in item_oids:
                    item_oids.append(it_oid)
                    self._create_itemref_object(vl, wc, dataset, variable, it_oid)
                    self._create_itemdef_object(vl, wc, define_objects, it_oid, variable)
                    wc_variable = wc["Clause"][0]["Values"][0]
                    wc_oid = self.generate_oid(["WC", dataset, variable, wc_variable])
                    self._create_whereclause_object(template, define_objects, wc, wc_oid, dataset)
                # just processing first where clause for now as some are in the wrong spot
                break

    def _create_whereclause_object(self, object, define_objects, wc, wc_oid, dataset):
        where_clause = WC.WhereClauses()
        where_clause.create_define_objects(object, define_objects, wc, wc_oid, dataset, self.lang, self.acrf)

    def _create_valuelistdef_object(self, oid, define_objects):
        """
        use the values from the VLM define-template to create a ValueListDef odmlib template
        """
        self.vld = DEFINE.ValueListDef(OID=oid)
        define_objects["ValueListDef"].append(self.vld)

    def _create_itemref_object(self, vl, wc, dataset, variable, it_oid):
        """
        use the values from the ValueLevel worksheet row to create ItemRef define_objects for ValueListDef
        """
        # will need to make this work with multiple where clauses in a future iteration
        wc_variable = wc["Clause"][0]["Values"][0]
        # mandatory missing - just hard code it for now
        mandatory = "No"
        attr = {"ItemOID": it_oid, "Mandatory": mandatory}
        if vl.get("Order"):
            attr["Order"] = vl["order"]
        if vl.get("Method"):
            attr["MethodOID"] = self.generate_oid(["MT", vl["Method"]])
        item = DEFINE.ItemRef(**attr)
        wc_oid = self.generate_oid(["WC", dataset, variable, wc_variable])
        wc = DEFINE.WhereClauseRef(WhereClauseOID=wc_oid)
        item.WhereClauseRef.append(wc)
        self.vld.ItemRef.append(item)

    def _create_itemdef_object(self, vl, wc, define_objects, it_oid, variable):
        """
        use the values from the VLM in the define-template to create ItemDef define_objects referenced by ValueListDef ItemRefs
        """
        if vl.get("dataType"):
            data_type = vl["dataType"]
        else:
            data_type = "text"
        # uses Char instead of Define-XML data type
        if data_type == "Char":
            data_type = "text"
        elif data_type == "Num":
            data_type = "float"
        attr = {"OID": it_oid, "Name": variable, "DataType": data_type}
        self._add_optional_itemdef_attributes(attr, vl, variable)
        item = DEFINE.ItemDef(**attr)
        self._add_optional_itemdef_elements(item, vl)
        define_objects["ItemDef"].append(item)

    def _add_optional_itemdef_elements(self, item, vl):
        """
        use the values from the VLM define-template to add the optional ELEMENTS to the ItemDef template
        """
        if vl.get("codeList"):
            cl = DEFINE.CodeListRef(CodeListOID=vl.get("codelist"))
            item.CodeListRef = cl
        if vl.get("originType"):
            # input only provides for 1 Origin, but multiple are supported by the spec
            attr = {"Type": vl["originType"]}
            if vl.get("originSource"):
                attr["Source"] = vl["originSource"]
            item.Origin.append(DEFINE.Origin(**attr))
            if vl.get("Predecessor"):
                item.Origin[0].Description = DEFINE.Description()
                item.Origin[0].Description.TranslatedText.append(DEFINE.TranslatedText(_content=vl["predecessor"]))
            if vl.get("pages"):
                dr = DEFINE.DocumentRef(leafID=self.acrf)
                dr.PDFPageRef.append(DEFINE.PDFPageRef(PageRefs=vl["pages"], Type="PhysicalRef"))
                item.Origin[0].DocumentRef.append(dr)


    def _add_optional_itemdef_attributes(self, attr, vl, variable):
        """
        use the values from the VLM define-template to add the optional attributes to the ItemDef template
        """
        if len(variable) < 9:
            attr["SASFieldName"] = variable
        else:
            print(f"Skipping SASFieldName for ItemDef {variable} because it exceeds the 8 character limit")
        if vl.get("Length"):
            attr["Length"] = vl["Length"]
        if vl.get("significantDigits"):
            attr["SignificantDigits"] = vl["significantDigits"]
        if vl.get("format"):
            attr["DisplayFormat"] = vl["format"]
        if vl.get("Comment"):
            attr["CommentOID"] = self.generate_oid(["COM", vl["Comment"]])
