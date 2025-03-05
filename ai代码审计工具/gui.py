import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QFileDialog, QComboBox,
                             QTabWidget, QGroupBox, QFormLayout, QMessageBox, QSplitter,
                             QDialog, QDialogButtonBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor

# 导入核心引擎和相关模块
try:
    from core_engine import CoreEngine
except ImportError:
    # 如果导入失败，尝试其他导入路径
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core_engine import CoreEngine

class AuditThread(QThread):
    """审计线程，用于在后台执行代码审计任务"""
    audit_complete = pyqtSignal(dict)
    audit_error = pyqtSignal(str)
    
    def __init__(self, core_engine, code_path):
        super().__init__()
        self.core_engine = core_engine
        self.code_path = code_path
        
    def run(self):
        try:
            result = self.core_engine.run_audit(self.code_path)
            self.audit_complete.emit(result)
        except Exception as e:
            self.audit_error.emit(str(e))

class CodeAuditGUI(QMainWindow):
    """代码审计工具的主窗口类"""
    def __init__(self):
        super().__init__()
        self.core_engine = CoreEngine()
        self.init_ui()
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志记录"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('AI代码审计工具 by：一个人挺好 项目已开源：https://github.com/hibody6666/ai-')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部控制区域
        control_group = QGroupBox('控制面板')
        control_layout = QHBoxLayout()
        
        # 代码路径选择
        self.path_edit = QTextEdit()
        self.path_edit.setMaximumHeight(60)
        self.path_edit.setPlaceholderText('请输入或选择代码路径')
        
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.browse_code_path)
        
        # AI模型选择和配置
        model_group = QGroupBox('AI模型配置')
        model_layout = QFormLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems(['ChatGPT', 'DeepSeek', 'Kimi', 'Ollama'])
        model_layout.addRow('选择模型:', self.model_combo)
        
        # API配置按钮
        config_btn = QPushButton('配置API')
        config_btn.clicked.connect(self.show_api_config)
        model_layout.addRow('API设置:', config_btn)
        
        model_group.setLayout(model_layout)
        model_group.setMaximumWidth(200)
        
        # 开始审计按钮
        self.audit_btn = QPushButton('开始审计')
        self.audit_btn.clicked.connect(self.start_audit)
        self.audit_btn.setMinimumHeight(40)
        
        # 赞助作者按钮
        sponsor_btn = QPushButton('赞助作者')
        sponsor_btn.clicked.connect(self.show_sponsor)
        sponsor_btn.setMinimumHeight(40)
        
        # 添加到控制布局
        control_layout.addWidget(self.path_edit, 3)
        control_layout.addWidget(browse_btn, 1)
        control_layout.addWidget(model_group, 1)
        control_layout.addWidget(self.audit_btn, 1)
        control_layout.addWidget(sponsor_btn, 1)
        control_group.setLayout(control_layout)
        
        # 创建分割器，用于结果显示区域
        splitter = QSplitter(Qt.Vertical)
        
        # 创建结果显示区域
        results_tabs = QTabWidget()
        
        # 审计结果标签页
        self.audit_result_text = QTextEdit()
        self.audit_result_text.setReadOnly(True)
        results_tabs.addTab(self.audit_result_text, '审计结果')
        
        # AI分析结果标签页
        self.ai_analysis_text = QTextEdit()
        self.ai_analysis_text.setReadOnly(True)
        results_tabs.addTab(self.ai_analysis_text, 'AI分析')
        
        # 综合报告标签页
        self.final_report_text = QTextEdit()
        self.final_report_text.setReadOnly(True)
        results_tabs.addTab(self.final_report_text, '综合报告')
        
        # 日志显示区域
        log_group = QGroupBox('日志')
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        # 添加到分割器
        splitter.addWidget(results_tabs)
        splitter.addWidget(log_group)
        splitter.setSizes([600, 200])
        
        # 添加到主布局
        main_layout.addWidget(control_group)
        main_layout.addWidget(splitter)
        
        # 设置状态栏
        self.statusBar().showMessage('就绪')
        
    def browse_code_path(self):
        """打开文件对话框选择代码路径"""
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(
            self, "选择代码目录", "", options=options
        )
        if directory:
            self.path_edit.setText(directory)
            self.logger.info(f'选择代码路径: {directory}')
            self.log_message(f'选择代码路径: {directory}')
    
    def start_audit(self):
        """开始代码审计流程"""
        code_path = self.path_edit.toPlainText().strip()
        if not code_path:
            QMessageBox.warning(self, '警告', '请先选择代码路径')
            return
        
        # 获取选择的AI模型
        selected_model = self.model_combo.currentText()
        
        # 更新状态
        self.statusBar().showMessage('正在审计...')
        self.audit_btn.setEnabled(False)
        self.log_message(f'开始审计，使用模型: {selected_model}')
        
        # 清空结果区域
        self.audit_result_text.clear()
        self.ai_analysis_text.clear()
        self.final_report_text.clear()
        
        # 创建并启动审计线程
        self.audit_thread = AuditThread(self.core_engine, code_path)
        self.audit_thread.audit_complete.connect(self.handle_audit_complete)
        self.audit_thread.audit_error.connect(self.handle_audit_error)
        self.audit_thread.start()
    
    def handle_audit_complete(self, result):
        """处理审计完成信号"""
        # 在实际应用中，这里需要根据result的结构来展示结果
        self.log_message('审计完成')
        
        # 示例：假设result包含audit_result、analysis_result和final_report
        if 'audit_result' in result:
            self.display_audit_result(result['audit_result'])
        
        if 'analysis_result' in result:
            self.display_ai_analysis(result['analysis_result'])
        
        if 'final_report' in result:
            self.display_final_report(result['final_report'])
        
        # 恢复状态
        self.statusBar().showMessage('审计完成')
        self.audit_btn.setEnabled(True)
    
    def handle_audit_error(self, error_msg):
        """处理审计错误信号"""
        self.log_message(f'审计出错: {error_msg}')
        QMessageBox.critical(self, '错误', f'审计过程中发生错误:\n{error_msg}')
        
        # 恢复状态
        self.statusBar().showMessage('审计失败')
        self.audit_btn.setEnabled(True)
    
    def display_audit_result(self, audit_result):
        """显示代码审计结果"""
        # 这里需要根据实际的audit_result结构来格式化显示
        self.audit_result_text.setHtml(self.format_result_as_html(audit_result, '代码审计结果'))
    
    def display_ai_analysis(self, analysis_result):
        """显示AI分析结果"""
        # 这里需要根据实际的analysis_result结构来格式化显示
        self.ai_analysis_text.setHtml(self.format_result_as_html(analysis_result, 'AI分析结果'))
    
    def display_final_report(self, final_report):
        """显示综合报告"""
        # 这里需要根据实际的final_report结构来格式化显示
        self.final_report_text.setHtml(self.format_result_as_html(final_report, '综合分析报告'))
    
    def format_result_as_html(self, result, title):
        """将结果格式化为HTML显示"""
        html = f"<h2>{title}</h2>"
        
        if not result:  # 如果结果为空
            return html + "<p>无数据</p>"
        
        # 这里需要根据实际的result结构来格式化
        # 示例实现
        html += "<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
        
        for key, value in result.items():
            html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
        
        html += "</table>"
        return html
    
    def log_message(self, message):
        """在日志区域添加消息"""
        self.log_text.append(message)
        # 滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def show_api_config(self):
        """显示API配置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle('API配置')
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # ChatGPT配置
        chatgpt_group = QGroupBox('ChatGPT')
        chatgpt_layout = QFormLayout()
        self.chatgpt_key = QLineEdit()
        self.chatgpt_base = QLineEdit('https://api.openai.com/v1')
        chatgpt_layout.addRow('API密钥:', self.chatgpt_key)
        chatgpt_layout.addRow('API地址:', self.chatgpt_base)
        chatgpt_group.setLayout(chatgpt_layout)
        layout.addRow(chatgpt_group)
        
        # DeepSeek配置
        deepseek_group = QGroupBox('DeepSeek')
        deepseek_layout = QFormLayout()
        self.deepseek_key = QLineEdit()
        self.deepseek_base = QLineEdit('https://api.deepseek.com/v1')
        deepseek_layout.addRow('API密钥:', self.deepseek_key)
        deepseek_layout.addRow('API地址:', self.deepseek_base)
        deepseek_group.setLayout(deepseek_layout)
        layout.addRow(deepseek_group)
        
        # Kimi配置
        kimi_group = QGroupBox('Kimi')
        kimi_layout = QFormLayout()
        self.kimi_key = QLineEdit()
        self.kimi_base = QLineEdit('https://api.moonshot.cn/v1')
        kimi_layout.addRow('API密钥:', self.kimi_key)
        kimi_layout.addRow('API地址:', self.kimi_base)
        kimi_group.setLayout(kimi_layout)
        layout.addRow(kimi_group)
        
        # Ollama配置
        ollama_group = QGroupBox('Ollama')
        ollama_layout = QFormLayout()
        self.ollama_base = QLineEdit('http://localhost:11434')
        ollama_layout.addRow('API地址:', self.ollama_base)
        ollama_group.setLayout(ollama_layout)
        layout.addRow(ollama_group)
        
        # 加载当前配置
        self.load_api_config()
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(lambda: self.save_api_config(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def load_api_config(self):
        """加载API配置"""
        config = self.core_engine.ai_models.config
        
        # ChatGPT配置
        chatgpt_config = config.get('chatgpt', {})
        self.chatgpt_key.setText(chatgpt_config.get('api_key', ''))
        self.chatgpt_base.setText(chatgpt_config.get('api_base', 'https://api.openai.com/v1'))
        
        # DeepSeek配置
        deepseek_config = config.get('deepseek', {})
        self.deepseek_key.setText(deepseek_config.get('api_key', ''))
        self.deepseek_base.setText(deepseek_config.get('api_base', 'https://api.deepseek.com/v1'))
        
        # Kimi配置
        kimi_config = config.get('kimi', {})
        self.kimi_key.setText(kimi_config.get('api_key', ''))
        self.kimi_base.setText(kimi_config.get('api_base', 'https://api.moonshot.cn/v1'))
        
        # Ollama配置
        ollama_config = config.get('ollama', {})
        self.ollama_base.setText(ollama_config.get('api_base', 'http://localhost:11434'))
    
    def save_api_config(self, dialog):
        """保存API配置"""
        config = {
            'chatgpt': {
                'api_key': self.chatgpt_key.text(),
                'api_base': self.chatgpt_base.text()
            },
            'deepseek': {
                'api_key': self.deepseek_key.text(),
                'api_base': self.deepseek_base.text()
            },
            'kimi': {
                'api_key': self.kimi_key.text(),
                'api_base': self.kimi_base.text()
            },
            'ollama': {
                'api_base': self.ollama_base.text()
            }
        }
        
        self.core_engine.ai_models.save_config(config)
        self.log_message('API配置已保存')
        dialog.accept()

    def show_sponsor(self):
        """显示赞助作者对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle('赞助作者')
        dialog.setFixedSize(300, 400)
        
        layout = QVBoxLayout()
        
        # 添加说明文本
        label = QLabel('如果觉得这个工具对您有帮助，欢迎赞助作者一杯咖啡 ☕')
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # 添加二维码图片
        qr_label = QLabel()
        qr_pixmap = QPixmap('sponsor_qr.png')
        qr_label.setPixmap(qr_pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)
        
        # 添加关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    window = CodeAuditGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()