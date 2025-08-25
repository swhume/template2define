from odmlib.define_2_1 import model as DEFINE
import define_object


class Study(define_object.DefineObject):
    """ create a Define-XML v2.1 Study element template and initialize the MetaDataVersion template """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, define_objects, lang, acrf):
        self.lang = lang
        self.acrf = acrf
        study_dict = {}
        for key, value in template.items():
            metadata = self._load_metadata(key, value)
            study_dict.update(metadata)
        if "Language" in study_dict:
            self.lang = study_dict["Language"]
        if "AnnotatedCRF" in study_dict:
            self.acrf = study_dict["Annotated CRF"]
        define_objects["Study"] = self._create_study_object(study_dict)
        define_objects["MetaDataVersion"] = self._create_metadataversion_object(study_dict)

    def _create_study_object(self, study_dict):
        """
        create the study ODMLIB template from the Study template and return it
        :param study_dict: dictionary created from the define-template study section
        :return: odmlib Study template
        """
        study_oid = self.generate_oid(['ODM', study_dict["StudyName"]])
        study = DEFINE.Study(OID=study_oid)
        gv = DEFINE.GlobalVariables()
        gv.StudyName = DEFINE.StudyName(_content=study_dict["StudyName"])
        gv.StudyDescription = DEFINE.StudyDescription(_content=study_dict.get("StudyDescription", "NA"))
        gv.ProtocolName = DEFINE.ProtocolName(_content=study_dict.get("ProtocolName", "NA"))
        study.GlobalVariables = gv
        return study

    def _create_metadataversion_object(self, study_dict):
        """
        create the MetaDataVersion ODMLIB template from the Study worksheet and return it
        :param study_dict: dictionary created from the study_dict in the study worksheet
        :return: odmlib MetaDataVersion template
        """
        mdv_oid = self.generate_oid(["MDV", study_dict["StudyName"]])
        mdv = DEFINE.MetaDataVersion(OID=mdv_oid, Name="MDV " + study_dict["StudyName"], Description="Data Definitions for "
                                                                                                     + study_dict["StudyName"], DefineVersion="2.1.0")
        return mdv

    def _load_metadata(self, key, value):
        """
        load the Study define-template content and return a dictionary
        :param key: index indicating the dictionary value to load
        :return: the value to load into the metadata dictionary
        """
        metadata = {}
        metadata[key] = value
        return metadata
