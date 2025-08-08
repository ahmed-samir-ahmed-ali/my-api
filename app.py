import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def get_link_metadata(url):
    metadata = {}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        metadata['error'] = f"فشل في جلب الرابط: {str(e)}"
        return metadata

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('meta', property='og:title')
    description = soup.find('meta', property='og:description')
    image = soup.find('meta', property='og:image')
    site_name = soup.find('meta', property='og:site_name')
    canonical_url = soup.find('meta', property='og:url')

    if not title:
        title = soup.find('title')
    if not description:
        description = soup.find('meta', attrs={'name': 'description'})

    metadata['title'] = title['content'] if title and 'content' in title.attrs else (title.text if title else 'لا يوجد عنوان')
    metadata['description'] = description['content'] if description and 'content' in description.attrs else 'لا يوجد وصف'
    metadata['image'] = image['content'] if image and 'content' in image.attrs else 'لا توجد صورة'
    metadata['site_name'] = site_name['content'] if site_name and 'content' in site_name.attrs else 'غير محدد'
    metadata['url'] = canonical_url['content'] if canonical_url and 'content' in canonical_url.attrs else url
    metadata['original_url'] = url

    return metadata

@app.route('/api/get-metadata', methods=['POST'])
def handle_get_metadata():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': "يجب تمرير 'url' في البيانات"}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'success': False, 'error': "الرابط لا يمكن أن يكون فارغًا"}), 400

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        metadata = get_link_metadata(url)
        if 'error' in metadata:
            return jsonify({'success': False, 'error': metadata['error']}), 400
        
        metadata['success'] = True
        return jsonify(metadata), 200

    except Exception as e:
        return jsonify({'success': False, 'error': f"خطأ في الخادم: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))