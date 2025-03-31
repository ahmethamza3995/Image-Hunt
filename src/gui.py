import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QProgressBar, 
                            QLabel, QMessageBox)
from PyQt6.QtCore import Qt
import os
from scrapper import download_images

class ImageDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Web Sitesi Görsel İndirici')
        self.setGeometry(100, 100, 600, 200)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # URL girişi için layout
        url_layout = QHBoxLayout()
        
        # URL etiketi
        url_label = QLabel('Website URL:')
        url_layout.addWidget(url_label)
        
        # URL giriş kutusu
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://example.com')
        url_layout.addWidget(self.url_input)
        
        # İndirme butonu
        self.download_btn = QPushButton('İndir')
        self.download_btn.clicked.connect(self.start_download)
        url_layout.addWidget(self.download_btn)
        
        layout.addLayout(url_layout)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Durum etiketi
        self.status_label = QLabel('')
        self.status_label.setWordWrap(True)  # Uzun metinlerin sarılmasını sağlar
        layout.addWidget(self.status_label)
        
        # Pencere stilini ayarla
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def start_download(self):
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, 'Hata', 'Lütfen bir URL girin.')
            return
            
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
            
        self.download_btn.setEnabled(False)
        self.status_label.setText('İndirme başlatılıyor...')
        self.progress_bar.setValue(0)
        
        try:
            # İndirme işlemini başlat
            folder_path, success, message = download_images(url, self.update_progress)
            
            if success:
                self.status_label.setText(f'İndirme tamamlandı. Klasör: {folder_path}')
                QMessageBox.information(self, 'Başarılı', 
                                      f'Görseller başarıyla indirildi.\nKonum: {folder_path}')
            else:
                self.status_label.setText(f'Hata: {message}')
                QMessageBox.critical(self, 'Hata', message)
                
        except Exception as e:
            self.status_label.setText(f'Hata oluştu: {str(e)}')
            QMessageBox.critical(self, 'Hata', f'İndirme sırasında hata oluştu: {str(e)}')
            
        finally:
            self.download_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    ex = ImageDownloaderGUI()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 