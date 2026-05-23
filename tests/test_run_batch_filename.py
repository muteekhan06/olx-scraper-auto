import unittest

from app.export_filenames import build_export_filename


class BatchExportFilenameTests(unittest.TestCase):
    def test_build_export_filename_keeps_generated_file_names_under_filesystem_limit(self):
        locations = (
            "dha defence,johar town,allama iqbal town,gulberg,bahria town,cantt,"
            "model town,sabzazar,township,wapda town,samanabad,faisal town,"
            "gulshan e ravi,gt road,askari,valencia town,raiwind road,shadbagh,"
            "jail road,mughalpura,park view villas,thokar niaz baig,bahria orchard,"
            "baghbanpura,pak arab housing,marghzar officers,harbanspura,"
            "chungi amar sadhu,gajju matah,garden town,daroghewala,ferozepur road,"
            "tajpura,lda avenue,walton road,maulana shaukat ali road,taj bagh"
        )

        filename = build_export_filename(locations, custom_search_url="")

        self.assertLessEqual(len(f"{filename}.xlsx"), 255)
        self.assertTrue(filename.startswith("olx_"))


if __name__ == "__main__":
    unittest.main()
