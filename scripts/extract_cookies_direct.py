# extract_cookies_direct.py
import os
import sys
import json
import shutil
import sqlite3
import ctypes
from ctypes import wintypes
from Crypto.Cipher import AES

# DPAPI Structures for CryptUnprotectData
class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]

def decrypt_dpapi(encrypted_data: bytes) -> bytes:
    """Decrypt data using Windows DPAPI CryptUnprotectData."""
    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    
    in_blob = DATA_BLOB()
    in_blob.cbData = len(encrypted_data)
    in_blob.pbData = (ctypes.c_byte * len(encrypted_data)).from_buffer_copy(encrypted_data)
    
    out_blob = DATA_BLOB()
    
    # Signatures: CryptUnprotectData(pDataIn, ppszDataDescr, pOptionalEntropy, pvReserved, pPromptStruct, dwFlags, pDataOut)
    success = CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob)
    )
    
    if not success:
        raise OSError("CryptUnprotectData failed.")
        
    result = bytes((ctypes.c_byte * out_blob.cbData).from_address(ctypes.addressof(out_blob.pbData.contents)))
    
    # Free memory allocated by CryptUnprotectData
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    
    return result

def get_master_key(local_state_path: str) -> bytes:
    """Get the master AES key from Local State file."""
    if not os.path.exists(local_state_path):
        raise FileNotFoundError(f"Local State not found at {local_state_path}")
        
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
        
    encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
    import base64
    encrypted_key = base64.b64decode(encrypted_key_b64)
    
    # Remove DPAPI prefix (first 5 bytes)
    encrypted_key = encrypted_key[5:]
    
    # Decrypt master key
    master_key = decrypt_dpapi(encrypted_key)
    return master_key

def decrypt_cookie_value(encrypted_value: bytes, master_key: bytes) -> str:
    """Decrypt an AES GCM encrypted cookie value."""
    try:
        if len(encrypted_value) > 3:
            # Only print first few to avoid log spam
            if not hasattr(decrypt_cookie_value, "printed"):
                decrypt_cookie_value.printed = 0
            if decrypt_cookie_value.printed < 5:
                print(f"[DEBUG] Cookie length={len(encrypted_value)} Prefix={encrypted_value[:10]}")
                decrypt_cookie_value.printed += 1
                
        if encrypted_value.startswith(b"v10") or encrypted_value.startswith(b"v11"):
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:]
            ciphertext = payload[:-16]
            tag = payload[-16:]
            
            cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted.decode("utf-8")
        else:
            # Fallback to DPAPI directly for older Chromium versions
            return decrypt_dpapi(encrypted_value).decode("utf-8")
    except Exception as e:
        print(f"[DEBUG] Decryption failed: {e}")
        return ""

def extract_cookies(user_data_dir: str, master_key: bytes) -> list:
    """Extract and decrypt cookies for target domains from profile default network cookies database."""
    cookies_db_path = os.path.join(user_data_dir, "Default", "Network", "Cookies")
    if not os.path.exists(cookies_db_path):
        # Retry with just "Cookies" (older Chromium versions)
        cookies_db_path = os.path.join(user_data_dir, "Default", "Cookies")
        if not os.path.exists(cookies_db_path):
            print(f"[EXTRACT] No cookies database found in {user_data_dir}")
            return []
            
    # Copy to temp file to bypass locks
    temp_db_path = "temp_cookies.db"
    shutil.copyfile(cookies_db_path, temp_db_path)
    
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    try:
        # Schema might differ slightly across versions. Select columns safely.
        cursor.execute("SELECT host_key, name, path, encrypted_value, expires_utc, is_secure, is_httponly, samesite FROM cookies")
        rows = cursor.fetchall()
        print(f"[EXTRACT] Debug: Total rows in database = {len(rows)}")
        sample_keys = sorted(list({r[0] for r in rows}))[:15]
        print(f"[EXTRACT] Debug: Sample host keys = {sample_keys}")
    except Exception as e:
        print(f"[EXTRACT] Failed to query cookies database: {e}")
        rows = []
    finally:
        conn.close()
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
            
    target_domains = {
        "copilot.microsoft.com",
        "bing.com",
        "login.live.com",
        "live.com",
        "login.microsoftonline.com",
        "microsoft.com"
    }
    
    decrypted_cookies = []
    samesite_map = {-1: "Lax", 0: "Lax", 1: "Strict", 2: "None"}
    
    for row in rows:
        host_key = row[0]
        
        # Check if the host key belongs to one of our target domains (matching subdomains as well)
        matched = False
        for target in target_domains:
            if host_key == target or host_key.endswith("." + target):
                matched = True
                break
                
        if not matched:
            continue
            
        name = row[1]
        path = row[2]
        encrypted_val = row[3]
        expires_utc = row[4]
        is_secure = bool(row[5])
        is_httponly = bool(row[6])
        samesite = samesite_map.get(row[7], "Lax")
        
        decrypted_val = decrypt_cookie_value(encrypted_val, master_key)
        if not decrypted_val:
            continue
            
        if expires_utc <= 0:
            expires = -1.0
        else:
            # Convert Windows Epoch to Unix Epoch
            expires = (expires_utc / 1000000.0) - 11644473600.0
            
        decrypted_cookies.append({
            "name": name,
            "value": decrypted_val,
            "domain": host_key,
            "path": path,
            "expires": expires,
            "httpOnly": is_httponly,
            "secure": is_secure,
            "sameSite": samesite
        })
        
    return decrypted_cookies

def main():
    print("=== DIRECT COPILOT COOKIE EXTRACTOR ===")
    
    chrome_user_data = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    edge_user_data = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
    
    candidates = [
        ("Microsoft Edge", edge_user_data),
        ("Google Chrome", chrome_user_data)
    ]
    
    all_extracted_cookies = []
    
    for name, user_data in candidates:
        local_state_path = os.path.join(user_data, "Local State")
        if not os.path.exists(local_state_path):
            print(f"[EXTRACT] Skipping {name}: Local State not found.")
            continue
            
        try:
            print(f"[EXTRACT] Reading master key for {name}...")
            master_key = get_master_key(local_state_path)
            
            print(f"[EXTRACT] Extracting cookies from {name} profile...")
            cookies = extract_cookies(user_data, master_key)
            if cookies:
                print(f"[EXTRACT] Found {len(cookies)} cookies for Copilot domains in {name}!")
                all_extracted_cookies.extend(cookies)
        except Exception as e:
            print(f"[EXTRACT] Failed to extract from {name}: {e}")
            
    if not all_extracted_cookies:
        print("[ERROR] No cookies could be extracted from any browser.")
        sys.exit(1)
        
    # Check if _C_Auth or other key cookies are present
    auth_cookies = [c for c in all_extracted_cookies if c["name"] == "_C_Auth" and c["value"]]
    print(f"\n[EXTRACT] Authentication cookies validated: Found {len(auth_cookies)} active _C_Auth cookies.")
    
    # Save to copilot_cookies.json
    output_path = "copilot_cookies.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_extracted_cookies, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Saved {len(all_extracted_cookies)} cookies to {output_path}!")
    
if __name__ == "__main__":
    main()
