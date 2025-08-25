from odmlib.define_2_1 import model as DEFINE
import define_object


""" Note: Methods have not yet been implemented in the template """
class Methods(define_object.DefineObject):
    """ create a Define-XML v2.1 MethodDef element """
    def __init__(self):
        super().__init__()

    def create_define_objects(self, template, define_objects, lang, acrf):
        """
        parse the define-template dictionary and create a odmlib define_objects to return in the define_objects dictionary
        :param template: define-template dictionary metadata
        :param define_objects: dictionary of odmlib define_objects updated by this method
        :param lang: xml:lang setting for TranslatedText
        :param acrf: part of the common interface but not used by this class
        """
        self.lang = lang
        define_objects["MethodDef"] = []
        for method in template:
            item = self._create_methoddef_object(method)
            define_objects["MethodDef"].append(item)

    def _create_methoddef_object(self, method):
        """
        use the values from the Methods section of the define-template to create a MethodDef odmlib ojbect
        :param method: Methods define-template dictionary section
        :return: a MethodDef odmlib template
        """
        attr = {"OID": method["OID"], "Name": method["Name"], "Type": method["Type"]}
        methoddef = DEFINE.MethodDef(**attr)
        tt = DEFINE.TranslatedText(_content=method["Description"], lang=self.lang)
        methoddef.Description = DEFINE.Description()
        methoddef.Description.TranslatedText.append(tt)
        if methoddef.get("Expression Context"):
            methoddef.FormalExpression.append(DEFINE.FormalExpression(Context=method["Expression Context"], _content=row["Expression Code"]))
        if method.get("Document"):
            self._add_document(method, methoddef)
        return method

    def _add_document(self, method, methoddef):
        """
        creates a DocumentRef template using metadata from the define-template dictionary
        :param method: Methods section in the define-template dictionary
        :param methoddef: odmlib MethodDef template that gets updated with a DocumentRef template
        """
        dr = DEFINE.DocumentRef(leafID=method["Document"])
        pdf = DEFINE.PDFPageRef(PageRefs=method["Pages"], Type="NamedDestination")
        dr.PDFPageRef.append(pdf)
        methoddef.DocumentRef.append(dr)
