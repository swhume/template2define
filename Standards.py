from odmlib.define_2_1 import model as DEFINE
import define_object


class Standards(define_object.DefineObject):
    """ create a Define-XML v2.1 Standards element template """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, define_objects, lang, acrf):
        """
        parse each value in the define-template and create odmlib define_objects to return in the define_objects dictionary
        :param template: define-template template section
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        standards = DEFINE.Standards()
        self.lang = lang
        for number, standard in enumerate(template, 1):
            std = self._create_standard_object(standard, number)
            standards.Standard.append(std)
        define_objects["Standards"] = standards

    def _create_standard_object(self, standard, number):
        """
        use the values from the Standards define-template dictionary to create a Standard odmlib template
        :param standard: Standards define-template dictionary section
        :return: odmlib Standard template
        """
        if "OID" not in standard:
            oid = self.generate_oid(["ST", str(number)])
        else:
            oid = standard["OID"]
        if "Status" not in standard:
            status = "Final"
        else:
            status = standard["Status"]
        attr = {"OID": oid, "Name": standard["Name"], "Type": standard["Type"], "Version": str(standard["Version"]),
                "Status": status}
        if standard.get("Publishing Set"):
            attr["PublishingSet"] = standard["Publishing Set"]
        if standard.get("Comment"):
            attr["CommentOID"] = standard["Comment"]
        return DEFINE.Standard(**attr)
