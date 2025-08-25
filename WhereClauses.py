from odmlib.define_2_1 import model as DEFINE
import define_object


class WhereClauses(define_object.DefineObject):
    """ create a Define-XML v2.1 WhereClauseDef element objects """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, define_objects, wc, wc_oid, dataset, lang, acrf):
        """
        parse the Excel template and create a odmlib define_objects to return in the define_objects dictionary
        :param template: content from the define-template
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param wc: WhereClause content from the define-template
        :param wc_oid: unique identifier for the WhereClause
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        wc_obj = wc["Clause"][0]
        wcd = self._create_whereclausedef_object(wc_obj, wc_oid, dataset)
        define_objects["WhereClauseDef"].append(wcd)
        rc = self._create_rangecheck(wc_obj, dataset)

    def _create_whereclausedef_object(self, wc, wc_oid, dataset):
        """
        use the values from the WhereClauses worksheet row to create a WhereClauseDef odmlib template
        :param row: WhereClauses worksheet row values as a dictionary
        :return: a WhereClause odmlib template
        """
        attr = {"OID": wc_oid}
        if wc.get("Comment"):
            attr["CommentOID"] = self.generate_oid(["COM", wc["Comment"]])
        where_clause = DEFINE.WhereClauseDef(**attr)
        it_oid = self.generate_oid(["IT", dataset, wc["Variable"]])
        rc_attr = {"SoftHard": "Soft", "ItemOID": it_oid, "Comparator": wc["Comparator"]}
        rc = DEFINE.RangeCheck(**rc_attr)
        if wc.get("Values"):
            for value in wc["Values"]:
                cv = DEFINE.CheckValue(_content=value)
                rc.CheckValue.append(cv)
        else:
            cv = DEFINE.CheckValue(_content="")
            rc.CheckValue.append(cv)
        where_clause.RangeCheck.append(rc)
        return where_clause

    def _create_rangecheck(self, wc, dataset):
        """
        use the values from the WhereClauses worksheet to create a RangeCheck odmlinb template
        :param row: WhereClauses worksheet row values as a dictionary
        :return: a RangeCheck odmlib template
        """
        item_oid = self.generate_oid(["IT", dataset, wc["Variable"]])
        rc_attr = {"SoftHard": "Soft", "ItemOID": item_oid, "Comparator": wc["Comparator"]}
        rc = DEFINE.RangeCheck(**rc_attr)
        for value in wc["Values"]:
            cv = DEFINE.CheckValue(_content=value)
            rc.CheckValue.append(cv)
        return rc
