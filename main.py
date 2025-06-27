import pandas as pd
import requests
import os
import re
from html import unescape
from bs4 import BeautifulSoup

# Function definitions
def is_valid_url(url):
    pattern = r'https://hiring\.base\.vn/opening/candidates/(\d+)\?stage=(\d+)$'
    return re.match(pattern, url) is not None

def extract_ids_from_url(url):
    match = re.search(r'candidates/(\d+)\?stage=(\d+)', url)
    if match:
        return match.group(1), match.group(2)
    return None, None

# Updated function to fetch candidates using stage_ids
def fetch_candidates_by_stages(opening_id, access_token):
    """
    Fetch candidates for specific stages of a job opening
    
    Parameters:
    opening_id (str): The ID of the opening
    access_token (str): The API access token
    
    Returns:
    dict: API response with candidate data
    """
    api_url = "https://hiring.base.vn/publicapi/v2/candidate/list"
    
    # Prepare the payload
    payload = {
        'access_token': access_token,
        'opening_id': opening_id,
        'num_per_page': '10000',
    }
        
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(api_url, headers=headers, data=payload)
    return response.json()

def fetch_jd(opening_id, access_token):
    api_url = "https://hiring.base.vn/publicapi/v2/opening/get"
    payload = {
        'access_token': access_token,
        'id': opening_id,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(api_url, headers=headers, data=payload)
    # Parse the JSON response
    json_response = response.json()
    
    # Get the 'content' field
    html_content = json_response.get('opening', {}).get('content', '')
    
    # Use BeautifulSoup to convert HTML content to plain text
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text = soup.get_text()
   
    return plain_text

# New function to get active stages for an opening
def get_opening_stages(opening_id, access_token):
    """Get active stages for a specific job opening"""
    api_url = "https://hiring.base.vn/publicapi/v2/opening/get"
    payload = {
        'access_token': access_token,
        'id': opening_id,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(api_url, headers=headers, data=payload)
    
    if response.status_code == 200:
        data = response.json()
        active_stages = [
            {"id": stage["id"], "name": stage["name"]}
            for stage in data.get("opening", {}).get("stats", {}).get("stages", [])
            if stage.get("state") == "active"
        ]
        return pd.DataFrame(active_stages)
    else:
        print(f"Lỗi khi lấy danh sách giai đoạn: {response.status_code} - {response.text}")
        return pd.DataFrame()

def extract_message(evaluations):
    """Extract text content from HTML evaluations"""
    if isinstance(evaluations, list) and len(evaluations) > 0:
        raw_html = evaluations[0].get('content', '')
        soup = BeautifulSoup(raw_html, "html.parser")
        return " ".join(soup.stripped_strings)
    return None  

def process_data(data):
    if 'candidates' not in data:
        print("Không tìm thấy ứng viên trong phản hồi.")
        return None
    df = pd.DataFrame(data['candidates'])
    
    # Convert cvs to first element if it exists
    if 'cvs' in df.columns:
        df['cvs'] = df['cvs'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    
    # Clean title if it exists
    if 'title' in df.columns:
        df['title'] = df['title'].apply(lambda x: re.sub(r'<.*?>', '', x) if isinstance(x, str) else x)
    
    # Unescape name if it exists
    if 'name' in df.columns:
        df['name'] = df['name'].apply(lambda x: unescape(x) if isinstance(x, str) else x)
    
    # Drop DOB columns if they exist
    dob_columns = ['dob_day', 'dob_month', 'dob_year']
    df_columns = df.columns.tolist()
    for col in dob_columns:
        if col in df_columns:
            df = df.drop(columns=[col])
    
    # Extract review from evaluations if it exists
    if 'evaluations' in df.columns:
        df['review'] = df['evaluations'].apply(extract_message)
    
    # Filter out rows without CVs if cvs column exists
    if 'cvs' in df.columns:
        df = df[df['cvs'].notnull()]
    
    # Drop columns with all null values
    df = df.dropna(axis=1, how='all')
    
    # List of columns to select (if they exist in the DataFrame)
    columns_to_select = ['id', 'name', 'gender', 'cvs', 'email', 'phone', 'form', 'stage_id']
    if 'review' in df.columns:
        columns_to_select.append('review')
    
    # Select only columns that exist in the DataFrame
    available_columns = [col for col in columns_to_select if col in df.columns]
    df = df[available_columns]
    
    # Process form data if it exists
    if 'form' in df.columns:
        form_data_list = df['form']
        # Convert each row in 'form' column to a dictionary
        form_df_list = []
        for form_data in form_data_list:
            if isinstance(form_data, list):
                data_dict = {item['id']: item['value'] for item in form_data}
                form_df_list.append(data_dict)
            else:
                form_df_list.append({})
        
        # Create new DataFrame from list of dictionaries
        form_df_transformed = pd.DataFrame(form_df_list)
        
        # Merge the original DataFrame (without 'form' column) with the transformed form data
        df_merged = pd.concat([df.drop(columns=['form']), form_df_transformed], axis=1)
        selected_df = df_merged
    else:
        selected_df = df
    df_cleaned = selected_df.dropna(axis=1, how='all')  # Xóa cột chứa toàn bộ giá trị None

    # Nếu muốn xóa cả cột chứa toàn bộ chuỗi rỗng
    df_cleaned = df_cleaned.loc[:, ~(df_cleaned == '').all()]
    
    return df_cleaned

# New function to get active job openings
def get_base_openings(access_token):
    """Retrieve active job openings from Base API"""
    url = "https://hiring.base.vn/publicapi/v2/opening/list"

    payload = {'access_token': access_token}
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        data = response.json()
        openings = data.get('openings', [])

        filtered_openings = [
            {"id": opening['id'], "name": opening['name']}
            for opening in openings if opening.get('status') == '10'
        ]
        return pd.DataFrame(filtered_openings)
    else:
        print(f"Lỗi khi lấy danh sách vị trí tuyển dụng: {response.status_code} - {response.text}")
        return pd.DataFrame()

# Function to convert empty strings to None
def convert_empty_to_none(df):
    """Convert empty strings to None in a pandas DataFrame"""
    # Replace empty strings with None in the entire DataFrame
    return df.replace('', None)

def get_candidates_data(opening_id, access_token, selected_stage_ids=None):
    """
    Main function to get candidates data as DataFrame
    
    Parameters:
    opening_id (str): The ID of the opening
    access_token (str): The API access token
    selected_stage_ids (list, optional): List of stage IDs to filter candidates
    
    Returns:
    pd.DataFrame: DataFrame containing candidates information
    """
    # Fetch candidates data
    raw_data = fetch_candidates_by_stages(opening_id, access_token)
    data = process_data(raw_data)
    
    if data is None or data.empty:
        print("Không thể lấy dữ liệu hoặc không tìm thấy ứng viên nào.")
        return pd.DataFrame()
    
    # Filter by stage_ids if provided
    if selected_stage_ids:
        data = data[data['stage_id'].isin(selected_stage_ids)]
    
    # Convert empty strings to None
    data = convert_empty_to_none(data)
    
    # Get stage information for mapping
    stages_df = get_opening_stages(opening_id, access_token)
    if not stages_df.empty:
        stages_mapping = dict(zip(stages_df['id'].astype(str), stages_df['name']))
        # Add stage name column if stage_id exists
        if 'stage_id' in data.columns:
            data['stage_name'] = data['stage_id'].astype(str).map(stages_mapping)
    
    # Add link to candidate profile
    if 'id' in data.columns:
        data['candidate_link'] = data['id'].apply(
            lambda x: f"https://hiring.base.vn/opening/{opening_id}?candidate={x}"
        )
    
    return data

# Example usage
if __name__ == "__main__":
    # Get BASE API Key from environment variable
    access_token = '5654-PTE7TTHBUKSU5W8XT2T3QDHRN7Y463A3T6ZDDP7DK95EZJBWSRLNLFKZNWKQGED4-FXYJZT6CBF89EEV2QYMNNDZZ7BSBU8KXJZTJJ643XZS8AWWBHUEE47MMAKC6GCRC'
    if not access_token:
        print("Không tìm thấy BASE_API_KEY trong biến môi trường.")
        exit()
    
    # Example: Get all job openings
    job_openings = get_base_openings(access_token)
    print("Danh sách job openings:")
    print(job_openings)
    
    # Example: Get candidates for a specific opening
    if not job_openings.empty:
        # Use the first job opening as example
        opening_id = job_openings['id'].iloc[0]
        print(f"\nLấy thông tin ứng viên cho opening_id: {opening_id}")
        
        # Get all candidates
        candidates_df = get_candidates_data(opening_id, access_token)
        print(f"Đã lấy {len(candidates_df)} ứng viên:")
        print(candidates_df.head())
        
        # Save to CSV
        candidates_df.to_csv('candidates_data.csv', index=False, encoding='utf-8-sig')
        print("Đã lưu dữ liệu vào file candidates_data.csv")
