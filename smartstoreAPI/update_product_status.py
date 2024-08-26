import json
import requests

def update_product_status():
    # 설정 파일에서 읽어오는 방식으로 개선 가능
    api_url = "https://api.example.com/update_product"  # 네이버 스마트스토어 API의 실제 URL로 교체해야 함
    access_token = "YOUR_ACCESS_TOKEN"  # 실제 네이버 스마트스토어 API의 액세스 토큰

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # JSON 파일 읽기
    with open('output.json', 'r') as file:
        products = json.load(file)

    for product in products:
        payload = {
            'product_code': product['code'],  # 제품 코드
            'availability': product['availability']  # 품절 여부
        }
        
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                print(f"Successfully updated product status: {product}")
            else:
                print(f"Failed to update product status. Status code: {response.status_code}. Response: {response.text}")
        except Exception as e:
            print(f"Error updating product status: {e}")

if __name__ == '__main__':
    update_product_status()
