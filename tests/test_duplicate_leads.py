import unittest
import sys
import types

sys.modules.setdefault("googleapiclient", types.ModuleType("googleapiclient"))
sys.modules.setdefault("googleapiclient.discovery", types.SimpleNamespace(build=lambda *args, **kwargs: None))

from app.google_sheets import (
    extract_lead_key,
    extract_link_from_formula,
    get_existing_lead_keys,
    remove_duplicate_leads,
)


class _FakeValues:
    def __init__(self, tab_values):
        self.tab_values = tab_values
        self.batch_requests = []

    def batchGet(self, spreadsheetId, ranges, valueRenderOption=None):
        self.batch_requests.append((tuple(ranges), valueRenderOption))
        value_ranges = []
        for range_name in ranges:
            title = range_name.split("!", 1)[0].strip("'")
            value_ranges.append({"range": range_name, "values": self.tab_values.get(title, [])})
        return types.SimpleNamespace(execute=lambda: {"valueRanges": value_ranges})


class _FakeSpreadsheets:
    def __init__(self, tabs, tab_values):
        self.tabs = tabs
        self.values_api = _FakeValues(tab_values)

    def get(self, spreadsheetId):
        sheets = [{"properties": {"title": title}} for title in self.tabs]
        return types.SimpleNamespace(execute=lambda: {"sheets": sheets})

    def values(self):
        return self.values_api


class _FakeService:
    def __init__(self, tabs, tab_values):
        self.spreadsheets_api = _FakeSpreadsheets(tabs, tab_values)

    def spreadsheets(self):
        return self.spreadsheets_api


class DuplicateLeadTests(unittest.TestCase):
    def test_extract_lead_key_prefers_ad_id(self):
        key = extract_lead_key({"Ad ID": " 123456789 ", "Link": "https://www.olx.com.pk/item/car-iid-999"})

        self.assertEqual(key, "ad:123456789")

    def test_extract_lead_key_falls_back_to_iid_url(self):
        key = extract_lead_key({"Link": "https://www.olx.com.pk/item/toyota-corolla-iid-1079361501"})

        self.assertEqual(key, "iid:1079361501")

    def test_extract_link_from_formula(self):
        link = extract_link_from_formula('=HYPERLINK("https://www.olx.com.pk/item/car-iid-123", "View Ad")')

        self.assertEqual(link, "https://www.olx.com.pk/item/car-iid-123")

    def test_remove_duplicate_leads_uses_history_and_current_batch(self):
        rows = [
            {"Ad ID": "111", "Title": "Already seen"},
            {"Ad ID": "222", "Title": "New"},
            {"Ad ID": "222", "Title": "Duplicate in same batch"},
            {"Link": "https://www.olx.com.pk/item/car-iid-333", "Title": "New by URL"},
            {"Link": "https://www.olx.com.pk/item/car-iid-333", "Title": "Duplicate URL"},
        ]

        output = remove_duplicate_leads(rows, existing_keys={"ad:111"})

        self.assertEqual([row["Title"] for row in output], ["New", "New by URL"])

    def test_get_existing_lead_keys_reads_prior_tabs_but_excludes_today(self):
        service = _FakeService(
            tabs=["21-05-2026", "22-05-2026", "23-05-2026", "Summary"],
            tab_values={
                "21-05-2026": [["Ad ID", "Link"], ["111", ""]],
                "22-05-2026": [["Title", "Link"], ["Toyota", '=HYPERLINK("https://www.olx.com.pk/item/car-iid-222", "View Ad")']],
                "23-05-2026": [["Ad ID", "Link"], ["333", ""]],
                "Summary": [["Ad ID"], ["444"]],
            },
        )

        keys = get_existing_lead_keys("sheet-id", exclude_sheet_name="23-05-2026", service=service)

        self.assertEqual(keys, {"ad:111", "iid:222"})
        self.assertEqual(
            service.spreadsheets_api.values_api.batch_requests,
            [(("'21-05-2026'!A:ZZ", "'22-05-2026'!A:ZZ"), "FORMULA")],
        )

    def test_get_existing_lead_keys_batches_many_tabs_to_avoid_read_quota(self):
        tabs = [f"{day:02d}-01-2026" for day in range(1, 62)]
        tab_values = {title: [["Ad ID"], [str(index)]] for index, title in enumerate(tabs, 1)}
        service = _FakeService(tabs=tabs, tab_values=tab_values)

        keys = get_existing_lead_keys("sheet-id", service=service)

        self.assertEqual(len(keys), 61)
        self.assertEqual(len(service.spreadsheets_api.values_api.batch_requests), 2)


if __name__ == "__main__":
    unittest.main()
