import json
from typing import Optional, List
from fastmcp import FastMCP

mcp = FastMCP("RICOH3504ex_MCP")

session = None
wim_token = None
cookies = None
current_printer_ip = None

import requests
from bs4 import BeautifulSoup
import base64
import urllib3
import ast
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@mcp.tool()
def login_printer(ip: str, username: str, password: str) -> str:
    """
    登录打印机并获取会话
    
    Args:
        ip: 打印机IP地址（必需）
        username: 登录用户名（必需）
        password: 登录密码（必需）
    
    Returns:
        str: 登录结果
    """
    global session, wim_token, cookies, current_printer_ip
    current_printer_ip = ip
    printer_username = username
    printer_password = password
    
    session = requests.Session()
    session.verify = False
    
    try:
        base_url = f'http://{ip}/web/guest/cn/websys/webArch'
        session.get(f'{base_url}/authForm.cgi', timeout=10).raise_for_status()
        response = session.get(f'{base_url}/authForm.cgi?open=websys/webArch/login.cgi', timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        wim_token = next((input_tag.get('value') for input_tag in soup.find_all('input') if input_tag.get('name') == 'wimToken'), None)
        login_form = next((form for form in soup.find_all('form') if 'login' in form.get('action', '').lower()), None)
        login_action = login_form.get('action', 'login.cgi') if login_form else 'login.cgi'
        form_data = {input_tag.get('name'): input_tag.get('value', '') for input_tag in login_form.find_all('input') if login_form and input_tag.get('name')}
        
        if wim_token:
            form_data['wimToken'] = wim_token
        
        form_data.update({
            'userid': base64.b64encode(printer_username.encode('utf-8')).decode('utf-8'),
            'password': base64.b64encode(printer_password.encode('utf-8')).decode('utf-8'),
            'userid_work': '',
            'password_work': ''
        })
        
        login_url = f'http://{ip}{login_action}' if login_action.startswith('/') else f'{base_url}/{login_action}'
        response = session.post(login_url, data=form_data, timeout=20, allow_redirects=False)
        
        if response.status_code in [302, 301, 303]:
            redirect_url = response.headers.get('Location', '')
            full_redirect_url = f'http://{ip}{redirect_url}' if redirect_url.startswith('/') else redirect_url
            session.get(full_redirect_url, timeout=10)
            
            try:
                address_list_url = f'http://{ip}/web/entry/cn/address/adrsList.cgi'
                address_list_response = session.get(address_list_url, timeout=10)
                address_list_response.raise_for_status()
                address_list_soup = BeautifulSoup(address_list_response.text, 'html.parser')
                wim_token = next((input_tag.get('value') for input_tag in address_list_soup.find_all('input') if input_tag.get('name') == 'wimToken'), wim_token)
            except:
                pass
            
            cookies = {cookie.name: cookie.value for cookie in session.cookies}
            return json.dumps({"success": True, "message": "登录成功"}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "message": "登录失败"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "message": f"登录失败: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_all_users() -> str:
    """
    获取打印机地址簿中的所有用户
    
    Returns:
        str: 用户列表JSON
    """
    if not session or not cookies or not wim_token or not current_printer_ip:
        return json.dumps({"success": False, "message": "请先登录", "users": [], "count": 0}, ensure_ascii=False)
    
    try:
        list_url = f"http://{current_printer_ip}/web/entry/cn/address/adrsListLoadEntry.cgi"
        params = {"_": "1", "listCountIn": "50", "getCountIn": "1"}
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-Requested-With': 'XMLHttpRequest'}
        response = session.get(list_url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return json.dumps({"success": False, "message": f"获取用户列表失败: HTTP {response.status_code}", "users": [], "count": 0}, ensure_ascii=False)
        
        data = None
        
        try:
            data = json.loads(response.text)
        except:
            try:
                data = ast.literal_eval(response.text)
            except:
                indices = re.findall(r'\[(\d+),\d+,\'(\d{5})\',\'([^\']*)\',\'([^\']*)\',\'([^\']*)\',\'([^\']*)\',\'([^\']*)\'\]', response.text)
                users = []
                for match in indices:
                    users.append({"index_num": int(match[0]), "index": match[1], "name": match[2], "email": match[5]})
                data = users if users else None
        
        if not data:
            return json.dumps({"success": False, "message": "解析用户列表失败", "users": [], "count": 0}, ensure_ascii=False)
        
        users = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list) and len(item) > 6:
                    user_name = str(item[3])
                    try:
                        user_name = user_name.encode('latin1').decode('utf-8')
                    except:
                        pass
                    users.append({"index_num": int(item[0]), "index": str(item[2]), "name": user_name, "email": str(item[6])})
        elif isinstance(data, dict) and 'data' in data:
            data_list = data['data']
            if isinstance(data_list, list):
                for item in data_list:
                    if isinstance(item, list) and len(item) > 6:
                        user_name = str(item[3])
                        try:
                            user_name = user_name.encode('latin1').decode('utf-8')
                        except:
                            pass
                        users.append({"index_num": int(item[0]), "index": str(item[2]), "name": user_name, "email": str(item[6])})
        
        return json.dumps({"success": True, "message": f"成功获取 {len(users)} 个用户", "users": users, "count": len(users)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "message": f"获取用户列表时发生错误: {str(e)}", "users": [], "count": 0}, ensure_ascii=False)

@mcp.tool()
def find_user_by_name(usernames: str) -> str:
    """
    根据用户名查找用户
    
    Args:
        usernames: 用户名或用户名列表
    
    Returns:
        str: 查找结果JSON
    """
    result = json.loads(get_all_users())
    if not result["success"]:
        return json.dumps({"success": False, "message": result["message"], "users": [], "count": 0}, ensure_ascii=False)
    
    if isinstance(usernames, str):
        usernames = [usernames]
    
    matched_users = []
    for user in result["users"]:
        user_name = user["name"]
        for username in usernames:
            if user_name == username:
                matched_users.append(user)
                break
            try:
                if user_name.encode('latin1').decode('utf-8') == username:
                    matched_users.append(user)
                    break
            except:
                continue
    
    return json.dumps({"success": len(matched_users) > 0, "message": f"找到 {len(matched_users)} 个匹配的用户", "users": matched_users, "count": len(matched_users)}, ensure_ascii=False)

@mcp.tool()
def add_user(username: str, email: str, user_index: Optional[str] = None) -> str:
    """
    添加用户到打印机地址簿
    
    Args:
        username: 用户名（必需）
        email: 邮箱（必需）
        user_index: 用户编号（可选，自动获取）
    
    Returns:
        str: 添加结果JSON
    """
    if not session or not cookies or not wim_token or not current_printer_ip:
        return json.dumps({"success": False, "message": "请先登录"}, ensure_ascii=False)
    
    try:
        get_wizard_url = f"http://{current_printer_ip}/web/entry/cn/address/adrsGetUserWizard.cgi"
        set_wizard_url = f"http://{current_printer_ip}/web/entry/cn/address/adrsSetUserWizard.cgi"
        
        if user_index is None:
            list_url = f"http://{current_printer_ip}/web/entry/cn/address/adrsListLoadEntry.cgi"
            params = {"_": "1", "listCountIn": "50", "getCountIn": "1"}
            response = session.get(list_url, params=params, timeout=10)
            
            try:
                data = json.loads(response.text)
                indices = []
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, list) and len(item) > 2:
                            index = str(item[2])
                            if index.isdigit() and len(index) == 5:
                                indices.append(int(index))
                if indices:
                    max_index = max(indices)
                    user_index = f"{max_index + 1:05d}"
                else:
                    user_index = "00001"
            except:
                user_index = "00001"
        
        step1_data = {"mode": "ADDUSER", "outputSpecifyModeIn": "DEFAULT", "wimToken": wim_token}
        response1 = session.post(get_wizard_url, data=step1_data, timeout=10)
        
        if response1.status_code != 200:
            return json.dumps({"success": False, "message": f"步骤1失败: {response1.status_code}"}, ensure_ascii=False)
        
        step2_data = [
            ("mode", "ADDUSER"), ("step", "BASE"), ("wimToken", wim_token),
            ("entryIndexIn", user_index), ("entryNameIn", username), ("entryDisplayNameIn", username),
            ("entryTagInfoIn", "1"), ("entryTagInfoIn", "1"), ("entryTagInfoIn", "1"), ("entryTagInfoIn", "1")
        ]
        response2 = session.post(set_wizard_url, data=step2_data, timeout=10)
        
        if response2.status_code != 200:
            return json.dumps({"success": False, "message": f"步骤2失败: {response2.status_code}"}, ensure_ascii=False)
        
        step3_data = [("mode", "ADDUSER"), ("step", "MAIL"), ("wimToken", wim_token), ("mailAddressIn", email)]
        response3 = session.post(set_wizard_url, data=step3_data, timeout=10)
        
        if response3.status_code != 200:
            return json.dumps({"success": False, "message": f"步骤3失败: {response3.status_code}"}, ensure_ascii=False)
        
        step4_data = [
            ("wimToken", wim_token), ("stepListIn", "BASE"), ("stepListIn", "MAIL"),
            ("mode", "ADDUSER"), ("step", "CONFIRM")
        ]
        response4 = session.post(set_wizard_url, data=step4_data, timeout=10)
        
        if response4.status_code != 200:
            return json.dumps({"success": False, "message": f"步骤4失败: {response4.status_code}"}, ensure_ascii=False)
        
        response_text = response4.text
        
        if user_index in response_text and email in response_text:
            return json.dumps({"success": True, "message": f"用户 {username} 添加成功", "user_index": user_index, "username": username, "email": email}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "message": "用户添加失败", "response_text": response_text[:500]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "message": f"添加用户时发生错误: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def delete_user(user_indices: str) -> str:
    """
    根据用户索引删除用户
    
    Args:
        user_indices: 用户索引或索引列表
    
    Returns:
        str: 删除结果JSON
    """
    if not session or not cookies or not wim_token or not current_printer_ip:
        return json.dumps({"success": False, "message": "请先登录", "deleted_count": 0, "deleted_indices": []}, ensure_ascii=False)
    
    try:
        if isinstance(user_indices, str):
            user_indices = [user_indices]
        
        result = json.loads(get_all_users())
        if not result["success"]:
            return json.dumps({"success": False, "message": result["message"], "deleted_count": 0, "deleted_indices": []}, ensure_ascii=False)
        
        users = result["users"]
        index_map = {user["index"]: user["index_num"] for user in users}
        
        index_nums = []
        for idx in user_indices:
            if idx in index_map:
                index_nums.append(str(index_map[idx]))
        
        if not index_nums:
            return json.dumps({"success": False, "message": "没有找到有效的用户索引", "deleted_count": 0, "deleted_indices": []}, ensure_ascii=False)
        
        delete_url = f"http://{current_printer_ip}/web/entry/cn/address/adrsDeleteEntries.cgi"
        entry_index_value = ",".join(index_nums) + ","
        files = {'entryIndex': (None, entry_index_value), 'wimToken': (None, wim_token)}
        headers = {"X-Requested-With": "XMLHttpRequest", "Referer": f"http://{current_printer_ip}/web/entry/cn/address/adrsList.cgi"}
        
        response = session.post(delete_url, files=files, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return json.dumps({"success": False, "message": f"删除失败: HTTP {response.status_code}", "deleted_count": 0, "deleted_indices": []}, ensure_ascii=False)
        
        response_text = response.text
        
        if '已成功删除' in response_text or '成功删除' in response_text:
            return json.dumps({"success": True, "message": f"成功删除 {len(user_indices)} 个用户", "deleted_count": len(user_indices), "deleted_indices": user_indices}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "message": "用户删除失败", "deleted_count": 0, "deleted_indices": [], "response_text": response_text[:500]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "message": f"删除用户时发生错误: {str(e)}", "deleted_count": 0, "deleted_indices": []}, ensure_ascii=False)

@mcp.tool()
def delete_user_by_name(usernames: str) -> str:
    """
    根据用户名删除用户
    
    Args:
        usernames: 用户名或用户名列表
    
    Returns:
        str: 删除结果JSON
    """
    result = json.loads(find_user_by_name(usernames))
    if not result["success"]:
        return json.dumps({"success": False, "message": result["message"], "deleted_count": 0, "deleted_indices": [], "deleted_names": []}, ensure_ascii=False)
    
    matched_users = result["users"]
    user_indices = [user["index"] for user in matched_users]
    
    if isinstance(usernames, str):
        usernames = [usernames]
    
    delete_result = json.loads(delete_user(user_indices))
    delete_result["deleted_names"] = usernames
    return json.dumps(delete_result, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
