from pathlib import Path
import json
from odmlib.define_2_1 import model as DEFINE
import define_object

class Conditions(define_object.DefineObject):
    """ create a Define-XML v2.1 WhereClauseDef element objects """
    def __init__(self):
        super().__init__()
        self.wc_stash_file = Path(__file__).parent.joinpath("wc_stash.json")

    def create_define_objects(self, template, define_objects, lang, acrf):
        """
        parse the Excel template and create a odmlib define_objects to return in the define_objects dictionary
        :param template: content from the define-template
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        conditions = []
        # stash the conditions created for use when generating WhereClauseDef
        for condition in template:
            rc = self._create_condition(condition)
            conditions.append({rc["OID"]: rc})
        with open(self.wc_stash_file, 'w') as f:
            json.dump(conditions, f, indent=4)

    @staticmethod
    def _create_condition(condition):
        condition_obj = {"OID": condition["OID"]}
        range_checks = []
        for rc in condition["rangeChecks"]:
            rc_attr = {"SoftHard": "Soft", "ItemOID": rc["item"], "Comparator": rc["comparator"]}
            check_values = []
            for value in rc["checkValues"]:
                check_values.append(value)
            rc_attr["CheckValue"] = check_values
            range_checks.append(rc_attr)
        condition_obj["RangeCheck"] = range_checks
        return condition_obj

    def _create_rangecheck(self, wc, dataset):
        """
        use the values from the WhereClauses worksheet to create a RangeCheck odmlib template
        :param wc: WhereClause
        :param dataset: dataset object
        :return: a RangeCheck odmlib template
        """
        item_oid = self.generate_oid(["IT", dataset, wc["Variable"]])
        rc_attr = {"SoftHard": "Soft", "ItemOID": item_oid, "Comparator": wc["Comparator"]}
        rc = DEFINE.RangeCheck(**rc_attr)
        for value in wc["Values"]:
            cv = DEFINE.CheckValue(_content=value)
            rc.CheckValue.append(cv)
        return rc
