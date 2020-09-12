import pdfquery
import unittest

class TestPDFRegression(unittest.TestCase):
    def test_compare_pdfs(self):
        pdf = pdfquery.PDFQuery("tests/IRS_1040A.pdf")
        pdf.load()
        i = pdf.pq[0].itertext()

        pdf2 = pdfquery.PDFQuery("tests/IRS_1040A2.pdf")
        pdf2.load()
        j = pdf.pq[0].itertext()

        for (t1,t2) in zip(i,j):
            self.assertEqual(t1,t2)

