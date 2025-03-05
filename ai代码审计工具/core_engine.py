import logging
from code_audit import CodeAudit
from ai_models import AIModels
from web_crawler import WebCrawler
from data_analysis import DataAnalysis

class CoreEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.code_audit = CodeAudit()
        self.ai_models = AIModels()
        self.web_crawler = WebCrawler()
        self.data_analysis = DataAnalysis()

    def run_audit(self, code_path):
        """
        执行代码审计流程
        """
        self.logger.info('Starting code audit process...')
        # 1. 爬取代码
        code_data = self.web_crawler.crawl(code_path)
        # 2. 调用AI模型分析
        analysis_result = self.ai_models.analyze(code_data)
        # 3. 执行代码审计
        audit_result = self.code_audit.audit(code_data)
        # 4. 数据分析
        final_report = self.data_analysis.analyze(audit_result, analysis_result)
        return final_report