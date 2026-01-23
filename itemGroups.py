from odmlib.define_2_1 import model as DEFINE
import define_object
import itemRefs
import valueLevel as VL


class ItemGroups(define_object.DefineObject):
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
        for dataset in template:
            if dataset.get("type", "Dataset") == "DataSpecialization":
                self._generate_vlm(dataset, define_objects, lang, acrf)
            else:
                self._generate_dataset(dataset, define_objects, lang, acrf)


    def _generate_vlm(self, dataset, define_objects, lang, acrf):
        vlm = VL.ValueLevel()
        vlm.create_define_objects(dataset, define_objects, lang, acrf)

    def _generate_dataset(self, dataset, define_objects, lang, acrf):
        itg = self._create_itemgroupdef_object(dataset)
        define_objects["ItemGroupDef"].append(itg)
        vars = itemRefs.ItemRefs()
        vars.create_define_objects(dataset["items"], define_objects, lang, acrf, item_group=itg)
        # assumption: 1 class per dataset - many need to expand this for ADaM
        if dataset.get("class"):
            ds_class = dataset["class"].upper().replace("-", " ")
            itg.Class = DEFINE.Class(Name=ds_class)

    def _create_itemgroupdef_object(self, obj):
        oid = self.generate_oid(["IG", obj["name"]])
        attr = {"OID": oid, "Name": obj["name"], "Domain": obj["name"]}
        if obj.get("archiveLocationID"):
            attr["ArchiveLocationID"] = ".".join(["LF", obj["archiveLocationID"]])
        attr["Structure"] = obj.get("structure", "NA")
        if obj.get("sasDatasetName"):
            attr["SASDatasetName"] = obj["sasDatasetName"]
        if obj.get("isReferenceData"):
            attr["IsReferenceData"] = obj["isReferenceData"]
        else:
            attr["IsReferenceData"] = self._generate_is_reference(attr)
        if obj.get("repeating"):
            if obj["repeating"]:
                attr["Repeating"] = "Yes"
            else:
                attr["Repeating"] = "No"
        else:
            attr["Repeating"] = self._generate_repeating_value(attr)
        # TODO how to tell if we're processing SDTM or ADaM define?
        if obj.get("purpose"):
            attr["Purpose"] = obj["purpose"]
        else:
            attr["Purpose"] = "Tabulation"

        if obj.get("comment"):
            attr["CommentOID"] = obj["comment"]
        if obj.get("isNonStandard"):
            attr["IsNonStandard"] = obj["isNonStandard"]
        # TODO derive this
        if obj.get("standardOID"):
            attr["StandardOID"] = obj["standardOID"]
        if obj.get("hasNoData"):
            attr["HasNoData"] = obj["hasNoData"]
        igd = DEFINE.ItemGroupDef(**attr)
        tt = DEFINE.TranslatedText(_content=obj["description"], lang=self.lang)
        igd.Description = DEFINE.Description()
        igd.Description.TranslatedText.append(tt)
        return igd

    def _generate_is_reference(self, attributes):
        """
        if the dataset is a trial design dataset, then IsReferenceData = "Yes"
        :param attributes:
        :return: str: "Yes" or "No"
        """
        if attributes["Domain"] in ["TA", "TD", "TE", "TI", "TM", "TS", "TV"]:
            return "Yes"
        else:
            return "No"

    def _generate_repeating_value(self, attributes) -> str:
        if attributes["IsReferenceData"] == "Yes":
            repeating = "No"
        elif attributes["Domain"] in ["DM", "APDM", "ADSL"]:
            repeating = "No"
        elif attributes["Domain"] in ["DI", "OI"]:
            # TODO check for presence of -PARMCD
            repeating = "No"
        elif attributes["Structure"] != "NA" and attributes["Structure"].count("per") == 1:
            repeating = "No"
        else:
            repeating = "Yes"
        return repeating
