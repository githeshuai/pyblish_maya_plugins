import pyblish.api
from maya import cmds


class ValidateNamespaceEmpty(pyblish.api.Validator):
    """Validate there are no empty namespaces in the scene.

    This is a scene wide validation that filters out "UI" and "shared"
    namespaces that exist by default in Maya and are mostly hidden.

    """

    families = ["model"]
    hosts = ["maya"]
    category = "scene"
    version = (0, 1, 0)
    label = "No Empty Namespaces"

    def process(self, context):
        """Process the Context"""
        all_namespaces = cmds.namespaceInfo(":",
                                            listOnlyNamespaces=True,
                                            recurse=True)
        non_internal_namespaces = [ns for ns in all_namespaces
                                   if ns not in ["UI", "shared"]]

        invalid = []
        # TODO: Check whether currently a namespace with
        # another namespace in it (both empty) is
        # considered empty
        for namespace in non_internal_namespaces:
            namespace_content = cmds.namespaceInfo(namespace,
                                                   listNamespace=True,
                                                   recurse=True)
            if not namespace_content:
                invalid.append(namespace)

        assert not invalid, (
            "Empty namespaces found: {0}".format(invalid))
