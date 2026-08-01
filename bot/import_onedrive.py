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

DEFAULT_ONEDRIVE_URL = "https://1drv.ms/x/c/1dfac0546fe61b6e/IQB_FD_q099EQ6DJiLVk6LybAQPVW1QpGIAgI_dR_IfRdR4?e=srRvlg"

def download_and_import_onedrive(
    onedrive_url: str = DEFAULT_ONEDRIVE_URL,
    db_file: str = "data/cultivation.db"
):
    """
    Downloads Excel file from OneDrive share link dynamically and imports player data directly into SQLite database.
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
        # Step 1: Open share link to establish session cookies and obtain redirect URL
        resp = opener.open(onedrive_url)
        final_url = resp.geturl()
        html = resp.read().decode('utf-8', errors='ignore')

        # Step 2: Dynamically extract UniqueId / sourcedoc
        doc_id = None
        match = re.search(r'sourcedoc=%7B([a-f0-9\-]+)%7D', final_url, re.IGNORECASE)
        if match:
            doc_id = match.group(1)
        else:
            match = re.search(r'UniqueId=([a-f0-9\-]+)', html, re.IGNORECASE)
            if match:
                doc_id = match.group(1)

        if not doc_id:
            # Fallback to known document ID if regex missed
            doc_id = "ea3f147f-dfd3-4344-a0c9-88b564e8bc9b"

        dl_url = f"https://onedrive.live.com/personal/1dfac0546fe61b6e/_layouts/15/download.aspx?UniqueId={doc_id}"
        logger.info(f"Đang tải dữ liệu OneDrive từ UniqueId: {doc_id}")

        with opener.open(dl_url) as dl_resp:
            data = dl_resp.read()
            if not data.startswith(b'PK'):
                raise ValueError("Tải file từ OneDrive thất bại, không nhận được file XLSX hợp lệ.")
            
            with open(temp_excel, "wb") as f:
                f.write(data)
            logger.info("Đã tải thành công file Excel mới từ OneDrive!")
    except Exception as e:
        logger.error(f"Lỗi khi tải OneDrive file: {e}")
        raise e

    # Step 3: Parse XLSX via zipfile
    with zipfile.ZipFile(temp_excel, 'r') as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for elem in tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                shared_strings.append(elem.text or '')

        sheet_files = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet')]
        if not sheet_files:
            raise ValueError("File Excel không chứa worksheet hợp lệ.")

        tree = ET.fromstring(z.read(sheet_files[0]))
        rows = []
        for row in tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row_vals = []
            for c in row.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                t = c.get('t')
                v_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                v = v_elem.text if v_elem is not None else ''
                if t == 's' and v != '':
                    v = shared_strings[int(v)]
                row_vals.append(v)
            if row_vals:
                rows.append(row_vals)

    if not rows or len(rows) < 2:
        logger.warning("File Excel không có dòng dữ liệu nhân vật nào.")
        return 0, 0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Ensure tables exist
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

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imported_players = 0
    imported_items = 0

    for row in rows[1:]:
        if len(row) < 3:
            continue
        discord_id = str(row[0]).strip()
        username = str(row[1]).strip() if len(row) > 1 else "Tu sĩ"
        ten = str(row[2]).strip() if len(row) > 2 and row[2] else username
        canh_gioi = str(row[3]).strip() if len(row) > 3 else "Luyện Khí tầng 1"
        try: exp = int(row[4])
        except: exp = 0
        try: linh_thach = int(row[5])
        except: linh_thach = 100
        linh_can = str(row[6]).strip() if len(row) > 6 else "Thiên Linh Căn"
        try: hp = int(row[7]) if len(row) > 7 else 100
        except: hp = 100
        try: mana = int(row[8]) if len(row) > 8 else 100
        except: mana = 100
        ngay_diem_danh = str(row[9]).strip() if len(row) > 9 else ""
        tui_do_str = str(row[10]).strip() if len(row) > 10 else "{}"
        try: buff_dot_pha = int(row[11]) if len(row) > 11 else 0
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
        """, (
            discord_id, ten, canh_gioi, exp, linh_thach, hp, mana, linh_can, ngay_diem_danh, buff_dot_pha, created_at
        ))
        imported_players += 1

        if tui_do_str.startswith("{"):
            try:
                inv_dict = json.loads(tui_do_str)
                for item_name, qty in inv_dict.items():
                    if int(qty) > 0:
                        cursor.execute("""
                            INSERT INTO inventory (discord_id, item_name, quantity)
                            VALUES (?, ?, ?)
                            ON CONFLICT(discord_id, item_name) DO UPDATE SET quantity = excluded.quantity
                        """, (discord_id, item_name, int(qty)))
                        imported_items += 1
            except Exception as e:
                logger.error(f"Lỗi parse túi đồ ID {discord_id}: {e}")

    conn.commit()
    conn.close()

    logger.info(f"Đã cập nhật thành công {imported_players} nhân vật & {imported_items} vật phẩm vào SQLite database ({db_file})!")
    return imported_players, imported_items

if __name__ == "__main__":
    download_and_import_onedrive()
