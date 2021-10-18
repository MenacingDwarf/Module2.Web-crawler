import unittest
from WebCrawler import WebCrawler

class BaseCrawlerTestCase(unittest.TestCase):
    url = ""
    total_num = 0
    internal_num = 0
    external_num = 0
        
    @classmethod
    def setUpClass(cls):
        print(f'Running Test Case: {cls.__name__}...')
        cls.crawler = WebCrawler(cls.url)
        cls.crawler.run(debug=False)
        
    def testValidTotalNum(self):
        self.assertEqual(len(self.crawler.full_urls), self.total_num)
        
    def testValidInternalsNum(self):
        self.assertEqual(len(self.crawler.get_internal_urls()), self.internal_num)
        
    def testValidExternalsNum(self):
        self.assertEqual(len(self.crawler.get_external_urls()), self.external_num)

class TestPortfolioWebsite(BaseCrawlerTestCase):
    url = "https://ascotbailey2.carbonmade.com/"
    total_num = 22
    internal_num = 9
    external_num = 13
        
        
class TestSlurpWebsite(BaseCrawlerTestCase):
    url = "https://ramenslurp.ru/"
    total_num = 9
    internal_num = 5
    external_num = 4        
        
def get_list_of_tests():
    return list(BaseCrawlerTestCase.__subclasses__())
    
def run_all_tests():
    loader = unittest.TestLoader()
    cases = []
    for cls in get_list_of_tests():
        cases.append(loader.loadTestsFromTestCase(cls))
    suite = unittest.TestSuite(cases)
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    
def run_single_test(test_case):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([loader.loadTestsFromTestCase(test_case)])
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
if __name__ == '__main__':
    unittest.main()
    
    