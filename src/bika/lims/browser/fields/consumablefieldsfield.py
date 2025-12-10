import copy

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from Products.Archetypes.Registry import registerField
from senaite.core.browser.fields.records import RecordsField
from bika.lims import api
from bika.lims.catalog import SETUP_CATALOG
from Products.Archetypes.public import DisplayList
from senaite.core import logger

class ConsumableFieldsField(RecordsField):
    """a list of Consumable field for services and analyses """
    _properties = RecordsField._properties.copy()
    _properties.update({
        "fixedSize": 0,
        "minimalSize": 0,
        "maximalSize": 9999,
        "type": "ConsumableFields",
        "subfields": (
            "keyword",
            "allow_empty",
        ),
        "subfield_labels": {
            "keyword": _("Keyword"),
            "allow_empty": _("Allow empty"),
        },
        "subfield_types": {
            "keyword": "string",
            "allow_empty": "boolean",
        },
        "subfield_sizes": {
            "keyword": 1,
        },
        "subfield_vocabularies": {
            "keyword": "_consumables_vocabulary",
        },
    })
    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        # local set consumables
        consumables = RecordsField.get(self, instance, **kwargs) or []

        # make sure we have a copy of the consumables field
        consumables = copy.deepcopy(consumables)
        return consumables

    def set(self, instance, value, **kwargs):
        # Freeze Consumable for Routine Analyses
        if IAnalysis.providedBy(instance):
            service = instance.getAnalysisService()

            if service:
                service_consumables = service.getConsumablesFields()
                keys = map(lambda v: v["keyword"], value)
                for inter in service_consumables:
                    if inter.get("keyword") in keys:
                        continue
                    value.append(inter)

        RecordsField.set(self, instance, value, **kwargs)
        
    def query_available_consumables(self):
        """Return all available Consumables
        """
        catalog = api.get_tool(SETUP_CATALOG)
        query = {
            "portal_type": "ReferenceDefinition",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        return catalog(query)

    def _consumables_vocabulary(self, *args, **kwargs):
        """Vocabulary used for allowed consumables field
        """
        consumables = self.query_available_consumables()

        items = [(api.get_uid(i), api.get_title(i)) for i in consumables]
        items = [("", _(""))] + items
        dlist = DisplayList(items)
        return dlist

registerField(
    ConsumableFieldsField,
    title="Consumable Fields",
    description="Used for storing Consumable Fields or Consumable Results")
