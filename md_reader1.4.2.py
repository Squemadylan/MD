#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD阅读器 v1.4.2 
修复：环境变量在导入 Qt 前设置，解决 GPU 渲染错误
"""

# ==================== 关键修复：必须在导入 Qt 前设置环境变量 ====================
import os
import sys

# GPU 设置：默认不设置，使用系统默认 GPU 加速
# 如果遇到启动问题或显示异常，可尝试以下设置：
# os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu-compositing --no-sandbox'
# os.environ['QT_OPENGL'] = 'software'

# ==================== 现在导入 Qt ====================
from pathlib import Path
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QToolBar, QStatusBar,
    QTabWidget, QFrame
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QFont


# 明亮主题
LIGHT_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MD阅读器</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background: #ffffff;
            padding: 40px;
            max-width: 900px;
            margin: 0 auto;
        }
        h1, h2, h3, h4, h5, h6 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; color: #1a1a1a; }
        h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: .875em; }
        h6 { font-size: .85em; color: #6a737d; }
        p { margin-bottom: 16px; }
        ul, ol { margin-bottom: 16px; padding-left: 2em; }
        li { margin-bottom: 4px; }
        li > ul, li > ol { margin-top: 4px; }
        input[type="checkbox"] { margin-right: 6px; }
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        strong { font-weight: 600; }
        em { font-style: italic; }
        code {
            background: rgba(175, 184, 193, 0.2);
            padding: .2em .4em;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, monospace;
            font-size: 85%;
        }
        pre {
            background: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin-bottom: 16px;
        }
        pre code { background: transparent; padding: 0; border-radius: 0; font-size: 100%; }
        blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            color: #6a737d;
            margin-bottom: 16px;
        }
        table { border-collapse: collapse; width: 100%; margin-bottom: 16px; display: block; overflow-x: auto; }
        th, td { border: 1px solid #dfe2e5; padding: 6px 13px; text-align: left; }
        th { background: #f6f8fa; font-weight: 600; }
        tr:nth-child(2n) { background: #f6f8fa; }
        hr { height: 4px; padding: 0; margin: 24px 0; background: #e1e4e8; border: 0; }
        img { max-width: 100%; height: auto; }
        .empty { text-align: center; color: #959da5; padding: 60px 20px; }
        .empty h2 { border: none; margin-bottom: 12px; }
        .empty p { font-size: 14px; line-height: 1.8; }
    </style>
</head>
<body>
    <div id="content">
        <div class="empty">
            <h2>📄 MD阅读器</h2>
            <p>点击「打开」加载 Markdown 文件<br>或直接拖拽 .md 文件到窗口</p>
        </div>
    </div>
    <script>
        window.addEventListener('load', function() {
            window.pageLoaded = true;
            if (window.pendingContent) {
                renderMarkdown(window.pendingContent);
                window.pendingContent = null;
            }
        });

        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true, gfm: true, headerIds: true, mangle: false,
                sanitize: false, smartLists: true, smartypants: true, xhtml: false,
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try { return hljs.highlight(code, { language: lang }).value; } catch (e) {}
                    }
                    return hljs.highlightAuto(code).value;
                }
            });
        }

        function renderMarkdown(content) {
            if (typeof marked === 'undefined') {
                window.pendingContent = content;
                return;
            }
            const html = marked.parse(content);
            document.getElementById('content').innerHTML = html;
            if (typeof hljs !== 'undefined') {
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        }

        function setEmpty() {
            document.getElementById('content').innerHTML = '<div class="empty"><h2>📄 MD阅读器</h2><p>点击「打开」加载 Markdown 文件<br>或直接拖拽 .md 文件到窗口</p></div>';
        }
    </script>
</body>
</html>'''

# 暗黑主题
DARK_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MD阅读器</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #c9d1d9;
            background: #0d1117;
            padding: 40px;
            max-width: 900px;
            margin: 0 auto;
        }
        h1, h2, h3, h4, h5, h6 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; color: #f0f6fc; }
        h1 { font-size: 2em; border-bottom: 1px solid #30363d; padding-bottom: .3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #30363d; padding-bottom: .3em; }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: .875em; }
        h6 { font-size: .85em; color: #8b949e; }
        p { margin-bottom: 16px; }
        ul, ol { margin-bottom: 16px; padding-left: 2em; }
        li { margin-bottom: 4px; }
        li > ul, li > ol { margin-top: 4px; }
        input[type="checkbox"] { margin-right: 6px; }
        a { color: #58a6ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        strong { font-weight: 600; }
        em { font-style: italic; }
        code {
            background: rgba(110, 118, 129, 0.4);
            padding: .2em .4em;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, monospace;
            font-size: 85%;
            color: #f0f6fc;
        }
        pre {
            background: #161b22;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin-bottom: 16px;
        }
        pre code { background: transparent; padding: 0; border-radius: 0; font-size: 100%; color: #f0f6fc; }
        blockquote {
            border-left: 4px solid #30363d;
            padding-left: 16px;
            color: #8b949e;
            margin-bottom: 16px;
        }
        table { border-collapse: collapse; width: 100%; margin-bottom: 16px; display: block; overflow-x: auto; }
        th, td { border: 1px solid #30363d; padding: 6px 13px; text-align: left; }
        th { background: #161b22; font-weight: 600; }
        tr:nth-child(2n) { background: #161b22; }
        hr { height: 4px; padding: 0; margin: 24px 0; background: #30363d; border: 0; }
        img { max-width: 100%; height: auto; }
        .empty { text-align: center; color: #8b949e; padding: 60px 20px; }
        .empty h2 { border: none; margin-bottom: 12px; color: #f0f6fc; }
        .empty p { font-size: 14px; line-height: 1.8; }
    </style>
</head>
<body>
    <div id="content">
        <div class="empty">
            <h2>📄 MD阅读器</h2>
            <p>点击「打开」加载 Markdown 文件<br>或直接拖拽 .md 文件到窗口</p>
        </div>
    </div>
    <script>
        window.addEventListener('load', function() {
            window.pageLoaded = true;
            if (window.pendingContent) {
                renderMarkdown(window.pendingContent);
                window.pendingContent = null;
            }
        });

        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true, gfm: true, headerIds: true, mangle: false,
                sanitize: false, smartLists: true, smartypants: true, xhtml: false,
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try { return hljs.highlight(code, { language: lang }).value; } catch (e) {}
                    }
                    return hljs.highlightAuto(code).value;
                }
            });
        }

        function renderMarkdown(content) {
            if (typeof marked === 'undefined') {
                window.pendingContent = content;
                return;
            }
            const html = marked.parse(content);
            document.getElementById('content').innerHTML = html;
            if (typeof hljs !== 'undefined') {
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        }

        function setEmpty() {
            document.getElementById('content').innerHTML = '<div class="empty"><h2>📄 MD阅读器</h2><p>点击「打开」加载 Markdown 文件<br>或直接拖拽 .md 文件到窗口</p></div>';
        }
    </script>
</body>
</html>'''


def is_windows_dark_mode():
    """检测 Windows 系统是否为暗黑模式"""
    try:
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except:
        return False


class MarkdownTab(QWidget):
    """单个标签页，包含一个 WebView"""
    def __init__(self, file_path=None, content="", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.content = content
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webview.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        
        layout.addWidget(self.webview)
        
    def set_theme(self, is_dark, callback=None):
        """设置主题，加载完成后回调"""
        template = DARK_TEMPLATE if is_dark else LIGHT_TEMPLATE
        self.webview.setHtml(template, QUrl("file:///"))
        if callback:
            # 增加延迟到 800ms，确保 CDN 资源加载完成
            QTimer.singleShot(800, callback)
    
    def render_content(self, content):
        """渲染 Markdown 内容 - 修复：添加延迟重试机制"""
        self.content = content
        escaped = content.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
        script = f"""
            (function() {{
                if (typeof renderMarkdown === 'function' && typeof marked !== 'undefined') {{
                    renderMarkdown('{escaped}');
                    return 'success';
                }} else {{
                    if (!window.pendingContent) window.pendingContent = '{escaped}';
                    return 'pending';
                }}
            }})()
        """
        
        def check_result(result):
            if result != 'success':
                QTimer.singleShot(200, lambda: self.render_content(content))
        
        self.webview.page().runJavaScript(script, check_result)
    
    def refresh(self):
        """刷新当前内容"""
        if self.file_path and os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.render_content(f.read())
                return True
            except:
                return False
        return False


class MarkdownEditor(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.is_dark_mode = is_windows_dark_mode()
        self.initial_file = initial_file
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("MD阅读器 v1.4.2")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        self.open_btn = QPushButton("📂 打开")
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.setFixedHeight(36)
        self.open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(self.open_btn)
        
        self.new_tab_btn = QPushButton("➕ 新标签")
        self.new_tab_btn.setCursor(Qt.PointingHandCursor)
        self.new_tab_btn.setFixedHeight(36)
        self.new_tab_btn.clicked.connect(self.new_tab)
        toolbar.addWidget(self.new_tab_btn)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.clicked.connect(self.refresh_current_tab)
        toolbar.addWidget(self.refresh_btn)
        
        self.close_tab_btn = QPushButton("❌ 关闭")
        self.close_tab_btn.setCursor(Qt.PointingHandCursor)
        self.close_tab_btn.setFixedHeight(36)
        self.close_tab_btn.clicked.connect(self.close_current_tab)
        toolbar.addWidget(self.close_tab_btn)
        
        self.theme_btn = QPushButton("🌙" if self.is_dark_mode else "☀️")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("切换暗黑/明亮模式")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_btn)
        
        toolbar.addSeparator()
        
        self.file_label = QLabel("未打开文件")
        self.file_label.setStyleSheet("font-size: 13px; margin-left: 16px; font-weight: 500;")
        toolbar.addWidget(self.file_label)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tab_widget)
        
        status = QStatusBar()
        self.setStatusBar(status)
        self.status_label = QLabel("就绪")
        status.addWidget(self.status_label)
        
        self.setAcceptDrops(True)
        
        # 如果有初始文件，直接打开；否则创建空白标签页
        if self.initial_file and Path(self.initial_file).exists():
            # 读取文件内容
            try:
                with open(self.initial_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.new_tab(self.initial_file, content)
            except Exception as e:
                print(f"读取初始文件失败: {e}")
                self.new_tab(self.initial_file)
        else:
            self.new_tab()
        
    def new_tab(self, file_path=None, content=""):
        """创建新标签页"""
        tab = MarkdownTab(file_path, content)
        
        def render_after_load():
            if content:
                tab.render_content(content)
        
        tab.set_theme(self.is_dark_mode, render_after_load)
        
        if file_path:
            tab_name = Path(file_path).name
            tab.file_path = file_path
        else:
            tab_name = "新标签"
        
        index = self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.setCurrentIndex(index)
        self.update_file_label()
        return tab
    
    def close_tab(self, index):
        """关闭指定标签页"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            tab = self.tab_widget.widget(0)
            if isinstance(tab, MarkdownTab):
                tab.file_path = None
                tab.content = ""
                tab.webview.page().runJavaScript("setEmpty()")
            self.tab_widget.setTabText(0, "新标签")
            self.update_file_label()
    
    def close_current_tab(self):
        """关闭当前标签页"""
        index = self.tab_widget.currentIndex()
        if index >= 0:
            self.close_tab(index)
    
    def on_tab_changed(self, index):
        """标签页切换事件"""
        self.update_file_label()
    
    def update_file_label(self):
        """更新文件标签"""
        tab = self.tab_widget.currentWidget()
        if isinstance(tab, MarkdownTab) and tab.file_path:
            self.file_label.setText(tab.file_path)
            self.status_label.setText(f"已打开: {Path(tab.file_path).name}")
        else:
            self.file_label.setText("未打开文件")
            self.status_label.setText("就绪")
    
    def open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 Markdown 文件", "",
            "Markdown Files (*.md *.markdown *.mdown);;All Files (*)"
        )
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """加载文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, MarkdownTab) and not current_tab.file_path and not current_tab.content:
                current_tab.file_path = file_path
                current_tab.render_content(content)
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), Path(file_path).name)
            else:
                self.new_tab(file_path, content)
            
            self.update_file_label()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件:\n{str(e)}")
    
    def refresh_current_tab(self):
        """刷新当前标签页"""
        tab = self.tab_widget.currentWidget()
        if isinstance(tab, MarkdownTab) and tab.file_path:
            try:
                with open(tab.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tab.render_content(content)
                self.status_label.setText(f"已刷新: {Path(tab.file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法刷新文件:\n{str(e)}")
    
    def toggle_theme(self):
        """切换主题"""
        self.is_dark_mode = not self.is_dark_mode
        self.theme_btn.setText("🌙" if self.is_dark_mode else "☀️")
        
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if isinstance(tab, MarkdownTab):
                content = tab.content
                tab.set_theme(self.is_dark_mode)
                if content:
                    QTimer.singleShot(300, lambda t=tab, c=content: t.render_content(c))
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.md', '.markdown', '.mdown')):
                self.load_file(file_path)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MD阅读器")
    app.setApplicationVersion("1.4.2")
    app.setStyle('Fusion')
    
    # 检查命令行参数，获取要打开的文件路径
    initial_file = None
    if len(sys.argv) > 1:
        # 支持多个文件，但默认打开第一个
        for arg in sys.argv[1:]:
            if not arg.startswith('-') and Path(arg).exists():
                initial_file = arg
                break
    
    window = MarkdownEditor(initial_file=initial_file)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
