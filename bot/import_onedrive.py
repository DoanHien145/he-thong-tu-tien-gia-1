import urllib.request
import http.cookiejar
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
import json
import os
import re
from datetime import datetime
from bot.logger import logger

DEFAULT_ONEDRIVE_URL = "https://excel.cloud.microsoft/open/onedrive/?docId=1DFAC0546FE61B6E%21s6246c65203524b4cb0a7e680ec5ac5ff&driveId=1DFAC0546FE61B6E"

def col_to_idx(col_str: str) -> int:
    idx = 0
    for char in col_str:
        idx = idx * 26 + (ord(char.upper()) - ord('A') + 1)
    return idx - 1

def parse_doc_id_from_url(url: str) -> str:
    """Tự động bóc tách UniqueId UUID từ URL OneDrive / Excel Cloud."""
    if not url:
        return ""
    # Format 1: %21s32hex or !s32hex
    match = re.search(r'(?:%21s|!s)([a-f0-9]{32})', url, re.IGNORECASE)
    if match:
        h = match.group(1)
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
    # Format 2: UniqueId=UUID
    match = re.search(r'UniqueId=([a-f0-9\-]{36})', url, re.IGNORECASE)
    if match:
        return match.group(1)
    # Format 3: sourcedoc=%7BUUID%7D
    match = re.search(r'sourcedoc=%7B([a-f0-9\-]+)%7D', url, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def download_and_import_onedrive(
    onedrive_url: str = DEFAULT_ONEDRIVE_URL,
    db_file: str = "data/cultivation.db"
):
    """
    Downloads Excel file from OneDrive share link dynamically and imports player data and inventory directly into SQLite database.
    Handles exact openxml cell positioning and multi-sheet structures (Players & Inventory).
    """
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    temp_excel = "data/onedrive_import_temp.xlsx"

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    ]

    try:
        # Luôn mở share link 1drv cơ sở trước để khởi tạo session cookies
        share_url = "https://1drv.ms/x/c/1dfac0546fe61b6e/IQC9j1b-bjt9T6mwEm3lLVsNAQujbSTEvbu_XQABciWtcNU?e=RGzo92"
        resp = opener.open(share_url)
        final_url = resp.geturl()
        html = resp.read().decode('utf-8', errors='ignore')

        candidates = []
        id1 = parse_doc_id_from_url(onedrive_url)
        if id1: candidates.append(id1)
        id2 = parse_doc_id_from_url(final_url)
        if id2 and id2 not in candidates: candidates.append(id2)
        id3 = parse_doc_id_from_url(html)
        if id3 and id3 not in candidates: candidates.append(id3)
        if "fe568fbd-3b6e-4f7d-a9b0-126de52d5b0d" not in candidates:
            candidates.append("fe568fbd-3b6e-4f7d-a9b0-126de52d5b0d")

        download_success = False
        for doc_id in candidates:
            dl_url = f"https://onedrive.live.com/personal/1dfac0546fe61b6e/_layouts/15/download.aspx?UniqueId={doc_id}"
            logger.info(f"Đang thử tải dữ liệu OneDrive từ UniqueId: {doc_id}")
            try:
                with opener.open(dl_url) as dl_resp:
                    data = dl_resp.read()
                    if data.startswith(b'PK'):
                        with open(temp_excel, "wb") as f:
                            f.write(data)
                        logger.info(f"Đã tải thành công file Excel mới từ OneDrive (UniqueId: {doc_id})!")
                        download_success = True
                        break
            except Exception as dl_err:
                logger.warning(f"Thử UniqueId {doc_id} thất bại: {dl_err}")

        if not download_success:
            raise ValueError("Tải file từ OneDrive thất bại, không nhận được file XLSX hợp lệ.")
    except Exception as e:
        logger.error(f"Lỗi khi tải OneDrive file: {e}")
        raise e

    # Step 3: Parse XLSX sheets with openxml cell coordinates
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA quick_check;")
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        logger.warning(f"Database {db_file} bị hỏng ({e}). Đang tái tạo lại file database mới...")
        try:
            conn.close()
        except Exception:
            pass
        for ext in ["", "-wal", "-shm", "-journal"]:
            f = db_file + ext
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as rem_err:
                    logger.error(f"Lỗi khi xóa file db {f}: {rem_err}")
        conn = sqlite3.connect(db_file)

    cursor = conn.cursor()

    # Ensure database schema exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            discord_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            canh_gioi TEXT NOT NULL,
            exp INTEGER NOT NULL DEFAULT 0,
            linh_thach INTEGER NOT NULL DEFAULT 100,
            hp INTEGER NOT NULL DEFAULT 100,
            mana INTEGER NOT NULL DEFAULT 100,
            linh_can TEXT NOT NULL,
            ngay_diem_danh TEXT DEFAULT '',
            buff_dot_pha INTEGER DEFAULT 0,
            cooldown_tu_luyen REAL DEFAULT 0,
            cooldown_sukien REAL DEFAULT 0,
            song_tu_partner TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            discord_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (discord_id, item_name)
        )
    """)

    imported_players = 0
    imported_items = 0

    with zipfile.ZipFile(temp_excel, 'r') as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for elem in tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                shared_strings.append(elem.text or '')

        sheet_files = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet')]
        if not sheet_files:
            raise ValueError("File Excel không chứa worksheet hợp lệ.")

        for sheet_file in sheet_files:
            tree = ET.fromstring(z.read(sheet_file))
            sheet_rows = []
            for row_elem in tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                row_cells = {}
                max_col = 0
                for c in row_elem.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    cell_ref = c.get('r')
                    if cell_ref:
                        col_str = ''.join([ch for ch in cell_ref if ch.isalpha()])
                        col_i = col_to_idx(col_str)
                    else:
                        col_i = max_col
                    max_col = max(max_col, col_i + 1)

                    t = c.get('t')
                    v_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    v = v_elem.text if v_elem is not None else ''
                    if t == 's' and v != '':
                        v = shared_strings[int(v)]
                    row_cells[col_i] = v.strip()

                row_vals = [row_cells.get(i, '') for i in range(max_col)]
                if any(row_vals):
                    sheet_rows.append(row_vals)

            if not sheet_rows:
                continue

            header = [h.lower() for h in sheet_rows[0]]

            # Detect Players Sheet
            if any('cảnh giới' in h or 'canh gioi' in h or 'exp' in h for h in header):
                col_map = {}
                for idx, h in enumerate(header):
                    if 'discord' in h or 'id' in h: col_map['discord_id'] = idx
                    elif 'tên' in h or 'ten' in h or 'name' in h: col_map['name'] = idx
                    elif 'cảnh giới' in h or 'canh gioi' in h: col_map['canh_gioi'] = idx
                    elif 'exp' in h or 'tu vi' in h: col_map['exp'] = idx
                    elif 'thạch' in h or 'thach' in h: col_map['linh_thach'] = idx
                    elif 'hp' in h: col_map['hp'] = idx
                    elif 'mana' in h: col_map['mana'] = idx
                    elif 'căn' in h or 'can' in h: col_map['linh_can'] = idx
                    elif 'điểm danh' in h or 'diem danh' in h: col_map['ngay_diem_danh'] = idx
                    elif 'buff' in h: col_map['buff_dot_pha'] = idx

                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                for r in sheet_rows[1:]:
                    def get_val(key, default=''):
                        idx = col_map.get(key)
                        if idx is not None and idx < len(r):
                            return r[idx]
                        return default

                    discord_id = get_val('discord_id')
                    if not discord_id or not discord_id.isdigit():
                        continue

                    name = get_val('name', 'Tu sĩ')
                    canh_gioi = get_val('canh_gioi', 'Luyện Khí tầng 1')

                    try: exp = int(get_val('exp', 0))
                    except: exp = 0

                    try: linh_thach = int(get_val('linh_thach', 100))
                    except: linh_thach = 100

                    try: hp = int(get_val('hp', 100))
                    except: hp = 100

                    try: mana = int(get_val('mana', 100))
                    except: mana = 100

                    linh_can = get_val('linh_can', 'Thiên Linh Căn')

                    ngay_diem_danh = get_val('ngay_diem_danh', '')
                    if ngay_diem_danh == '{}' or not ngay_diem_danh.startswith('20'):
                        ngay_diem_danh = ''

                    try: buff_dot_pha = int(get_val('buff_dot_pha', 0))
                    except: buff_dot_pha = 0

                    cursor.execute("""
                        INSERT INTO players (
                            discord_id, name, canh_gioi, exp, linh_thach, hp, mana, linh_can, ngay_diem_danh, buff_dot_pha, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(discord_id) DO UPDATE SET
                            name = excluded.name,
                            canh_gioi = excluded.canh_gioi,
                            exp = excluded.exp,
                            linh_thach = excluded.linh_thach,
                            hp = excluded.hp,
                            mana = excluded.mana,
                            linh_can = excluded.linh_can,
                            ngay_diem_danh = excluded.ngay_diem_danh,
                            buff_dot_pha = excluded.buff_dot_pha
                    """, (discord_id, name, canh_gioi, exp, linh_thach, hp, mana, linh_can, ngay_diem_danh, buff_dot_pha, created_at))
                    imported_players += 1

            # Detect Inventory Sheet
            elif any('vật phẩm' in h or 'vat pham' in h for h in header):
                inv_map = {}
                for idx, h in enumerate(header):
                    if 'discord' in h or 'id' in h: inv_map['discord_id'] = idx
                    elif 'vật phẩm' in h or 'vat pham' in h or 'item' in h: inv_map['item_name'] = idx
                    elif 'số lượng' in h or 'so luong' in h or 'qty' in h: inv_map['quantity'] = idx

                for r in sheet_rows[1:]:
                    discord_id = r[inv_map['discord_id']] if 'discord_id' in inv_map and inv_map['discord_id'] < len(r) else ''
                    item_name = r[inv_map['item_name']] if 'item_name' in inv_map and inv_map['item_name'] < len(r) else ''
                    try: qty = int(r[inv_map['quantity']]) if 'quantity' in inv_map and inv_map['quantity'] < len(r) else 0
                    except: qty = 0

                    if discord_id and item_name and qty > 0:
                        cursor.execute("""
                            INSERT INTO inventory (discord_id, item_name, quantity)
                            VALUES (?, ?, ?)
                            ON CONFLICT(discord_id, item_name) DO UPDATE SET quantity = excluded.quantity
                        """, (discord_id, item_name, qty))
                        imported_items += 1

    conn.commit()
    conn.close()

    logger.info(f"Đã cập nhật thành công {imported_players} nhân vật & {imported_items} vật phẩm vào SQLite database ({db_file})!")
    return imported_players, imported_items

if __name__ == "__main__":
    download_and_import_onedrive()

