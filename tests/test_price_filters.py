import unittest
import sys
import types
from urllib.parse import parse_qs, urlsplit

sys.modules.setdefault("bs4", types.SimpleNamespace(BeautifulSoup=object))
sys.modules.setdefault("selenium", types.ModuleType("selenium"))
sys.modules.setdefault("selenium.webdriver", types.SimpleNamespace(Chrome=object))
sys.modules.setdefault("selenium.webdriver.common", types.ModuleType("selenium.webdriver.common"))
sys.modules.setdefault("selenium.webdriver.common.by", types.SimpleNamespace(By=object))
sys.modules.setdefault("selenium.webdriver.support", types.ModuleType("selenium.webdriver.support"))
sys.modules.setdefault("selenium.webdriver.support.expected_conditions", types.SimpleNamespace())
sys.modules.setdefault("selenium.webdriver.support.ui", types.SimpleNamespace(WebDriverWait=object))
sys.modules.setdefault(
    "selenium.common.exceptions",
    types.SimpleNamespace(
        TimeoutException=Exception,
        StaleElementReferenceException=Exception,
        WebDriverException=Exception,
    ),
)
sys.modules.setdefault("app.driver", types.SimpleNamespace(build_driver=lambda *args, **kwargs: None))

from app.scraper import (
    build_list_page_url,
    listing_matches_price_filters,
    parse_filter_tokens,
    price_bounds_from_filter_tokens,
)


class PriceFilterTests(unittest.TestCase):
    def test_build_list_page_url_appends_price_bracket_filters(self):
        url = build_list_page_url(
            "https://www.olx.com.pk/dha-defence_g9/cars_c84",
            page=1,
            extra_filter_tokens=["price_min_1000000", "price_max_5000000"],
        )

        params = parse_qs(urlsplit(url).query)
        self.assertEqual(params["filter"], ["price_min_1000000,price_max_5000000"])

    def test_build_list_page_url_preserves_price_filters_with_pagination(self):
        url = build_list_page_url(
            "https://www.olx.com.pk/dha-defence_g9/cars_c84?filter=make_eq_toyota",
            page=2,
            extra_filter_tokens=["price_min_1000000", "price_max_5000000"],
        )

        params = parse_qs(urlsplit(url).query)
        self.assertEqual(params["filter"], ["make_eq_toyota,price_min_1000000,price_max_5000000"])
        self.assertEqual(params["page"], ["2"])

    def test_parse_filter_tokens_accepts_price_bracket_from_query_string(self):
        tokens = parse_filter_tokens("?filter=price_min_1000000,price_max_5000000")

        self.assertEqual(tokens, ["price_min_1000000", "price_max_5000000"])

    def test_price_bounds_from_filter_tokens(self):
        bounds = price_bounds_from_filter_tokens(["price_min_1000000", "price_max_5000000"])

        self.assertEqual(bounds, (1000000, 5000000))

    def test_listing_matches_price_filters_accepts_in_range_formatted_price(self):
        self.assertTrue(
            listing_matches_price_filters(
                {"Title": "Toyota Corolla", "Price": "Rs 2,390,000"},
                (1000000, 5000000),
            )
        )

    def test_listing_matches_price_filters_rejects_out_of_range_price(self):
        self.assertFalse(
            listing_matches_price_filters(
                {"Title": "Toyota Corolla", "Price": "Rs 7,500,000"},
                (1000000, 5000000),
            )
        )

    def test_listing_matches_price_filters_rejects_blocked_or_unpriced_rows(self):
        self.assertFalse(
            listing_matches_price_filters(
                {"Title": "Error1015", "Price": ""},
                (1000000, 5000000),
            )
        )


if __name__ == "__main__":
    unittest.main()
