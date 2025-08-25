from odmlib.define_2_1 import model as DEFINE
import define_object
import Variables


class Datasets(define_object.DefineObject):
    """ create a Define-XML v2.1 ItemGroupDef element template """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, define_objects, lang, acrf):
        """
        parse each row in the Excel template and create odmlib define_objects to return in the define_objects dictionary
        :param template: dataset section of the define-template
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: annotated case report form document
        """
        self.lang = lang
        for name, dataset in template.items():
            itg = self._create_itemgroupdef_object(name, dataset)
            define_objects["ItemGroupDef"].append(itg)
            vars = Variables.Variables()
            vars.create_define_objects(dataset["Variables"], define_objects, itg, lang, acrf)

    def _create_itemgroupdef_object(self, name, obj):
        oid = self.generate_oid(["IG", name])
        attr = {"OID": oid, "Name": name, "Domain": name, "SASDatasetName": name,
                "Structure": obj["Structure"], "ArchiveLocationID": ".".join(["LF", name])}
        if obj.get("Repeating"):
            attr["Repeating"] = obj["Repeating"]
        else:
            # temp value needed as Repeating is required in ItemGroupDef and not in template
            attr["Repeating"] = "No"
        if obj.get("IsReferenceData"):
            attr["IsReferenceData"] = obj["IsReferenceData"]
        if obj.get("Purpose"):
            attr["Purpose"] = obj["Purpose"]
        if obj.get("Comment"):
            attr["CommentOID"] = obj["Comment"]
        if obj.get("IsNonStandard"):
            attr["IsNonStandard"] = obj["IsNonStandard"]
        if obj.get("StandardOID"):
            attr["StandardOID"] = obj["StandardOID"]
        if obj.get("HasNoData"):
            attr["HasNoData"] = obj["HasNoData"]
        igd = DEFINE.ItemGroupDef(**attr)
        tt = DEFINE.TranslatedText(_content=obj["Description"], lang=self.lang)
        igd.Description = DEFINE.Description()
        igd.Description.TranslatedText.append(tt)
        # assumption: 1 class per dataset - many need to expand this for ADaM
        if obj.get("Class"):
            ds_class = obj["Class"].upper().replace("-", " ")
            igd.Class = DEFINE.Class(Name=ds_class)
        return igd
