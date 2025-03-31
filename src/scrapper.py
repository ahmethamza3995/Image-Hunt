import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import imghdr
import re
import time

def get_domain_name(url):
    """URL'den domain adını çıkarır"""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def download_image(url, image_url):
    """Görseli belirtilen URL'nin domain adına göre klasörleyerek indirir"""
    domain = get_domain_name(url)
    
    # Ana indirme klasörünü oluştur
    base_download_dir = os.path.join('data', 'downloaded')
    os.makedirs(base_download_dir, exist_ok=True)
    
    # Site için alt klasör oluştur
    site_download_dir = os.path.join(base_download_dir, domain)
    os.makedirs(site_download_dir, exist_ok=True)
    
    # Görsel dosya adını al
    image_name = os.path.basename(urlparse(image_url).path)
    if not image_name:
        image_name = f"image_{int(time.time())}.jpg"
    
    # Tam dosya yolunu oluştur
    file_path = os.path.join(site_download_dir, image_name)
    
    # Görseli indir
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path
    return None

def download_images(url, progress_callback=None):
    """
    Web sitesindeki resimleri indirir
    progress_callback: İlerleme durumunu bildirmek için kullanılacak fonksiyon
    """
    domain = get_domain_name(url)
    folder_path = os.path.join('data', 'downloaded', domain)
    
    # Klasör oluştur
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    try:
        # Web sayfasını al
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tüm img etiketlerini ve svg etiketlerini bul
        images = soup.find_all(['img', 'svg'])
        
        # CSS'teki background-image URL'lerini bul
        style_tags = soup.find_all('style')
        css_images = []
        for style in style_tags:
            if style.string:
                urls = re.findall(r'url\([\'"]?([^\'"]*)[\'"]?\)', style.string)
                css_images.extend(urls)

        total_images = len(images) + len(css_images)
        current_count = 0
        
        # Normal img etiketlerini işle
        for img in images:
            if img.name == 'img':
                img_url = img.get('src')
                if img_url:
                    current_count = download_single_image(img_url, url, folder_path, current_count)
            elif img.name == 'svg':
                try:
                    final_path = os.path.join(folder_path, f'image_{current_count}.svg')
                    with open(final_path, 'w', encoding='utf-8') as f:
                        f.write(str(img))
                    current_count += 1
                except Exception as e:
                    print(f'Hata: SVG kaydedilemedi - {str(e)}')
            
            if progress_callback:
                progress = (current_count / total_images) * 100
                progress_callback(int(progress))

        # CSS'ten bulunan resimleri işle
        for css_url in css_images:
            current_count = download_single_image(css_url, url, folder_path, current_count)
            if progress_callback:
                progress = (current_count / total_images) * 100
                progress_callback(int(progress))
                
        return folder_path, True, "İndirme tamamlandı"
        
    except Exception as e:
        return None, False, f"Hata oluştu: {str(e)}"

def download_single_image(img_url, base_url, folder_path, image_count):
    # Göreceli URL'leri mutlak URL'lere çevir
    img_url = urljoin(base_url, img_url)
    
    try:
        # Resmi indir
        response = requests.get(img_url)
        
        # Önce geçici bir dosyaya kaydedelim
        temp_path = os.path.join(folder_path, f'temp_{image_count}')
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # SVG kontrolü
        if 'image/svg+xml' in response.headers.get('content-type', '').lower() or img_url.lower().endswith('.svg'):
            ext = '.svg'
        else:
            # Gerçek formatı tespit edelim
            real_format = imghdr.what(temp_path)
            if real_format:
                ext = f'.{real_format}'
            else:
                # Format tespit edilemezse content-type'a bakalım
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
                    ext = '.jpg'
                elif 'png' in content_type.lower():
                    ext = '.png'
                elif 'gif' in content_type.lower():
                    ext = '.gif'
                elif 'webp' in content_type.lower():
                    ext = '.webp'
                else:
                    ext = '.jpg'
        
        # Doğru uzantı ile yeniden adlandıralım
        final_path = os.path.join(folder_path, f'image_{image_count}{ext}')
        os.rename(temp_path, final_path)
        print(f'İndirildi: image_{image_count}{ext}')
        
    except Exception as e:
        print(f'Hata: {img_url} indirilemedi - {str(e)}')
        # Hata durumunda geçici dosyayı temizleyelim
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return image_count + 1

# Kullanım örneği
url = 'https://www.google.com'
folder_path = '..data/downloaded_images'
download_images(url, folder_path)
