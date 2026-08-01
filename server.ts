import express from "express";
import path from "path";
import fs from "fs";
import { createServer as createViteServer } from "vite";
import ExcelJS from "exceljs";
import Groq from "groq-sdk";
import JSZip from "jszip";

const app = express();
const PORT = 3000;

app.use(express.json());

const EXCEL_FILE_PATH = path.join(process.cwd(), "data", "data.xlsx");

// Ensure data folder and Excel file exist with proper columns and NO mock disciples
async function ensureExcelExists(forceReset = false) {
  const dir = path.dirname(EXCEL_FILE_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const createCleanExcel = async () => {
    const workbook = new ExcelJS.Workbook();
    workbook.creator = "TongMonBot";
    workbook.lastModifiedBy = "TongMonBot";
    workbook.created = new Date();
    workbook.modified = new Date();

    const sheet = workbook.addWorksheet("TuSi", {
      views: [{ state: "frozen", ySplit: 1 }]
    });

    sheet.columns = [
      { header: "DiscordID", key: "DiscordID", width: 22 },
      { header: "Username", key: "Username", width: 22 },
      { header: "Tên", key: "Tên", width: 22 },
      { header: "Cảnh giới", key: "Cảnh giới", width: 22 },
      { header: "EXP", key: "EXP", width: 15 },
      { header: "Linh thạch", key: "Linh thạch", width: 15 },
      { header: "Linh căn", key: "Linh căn", width: 22 },
      { header: "HP", key: "HP", width: 12 },
      { header: "Mana", key: "Mana", width: 12 },
      { header: "Ngày điểm danh", key: "Ngày điểm danh", width: 20 },
      { header: "Túi đồ", key: "Túi đồ", width: 35 },
      { header: "Buff đột phá", key: "Buff đột phá", width: 15 }
    ];

    // Header styling for MS Excel compatibility
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: "FFFFFFFF" } };
    headerRow.fill = {
      type: "pattern",
      pattern: "solid",
      fgColor: { argb: "FF2D4D3D" }
    };

    await workbook.xlsx.writeFile(EXCEL_FILE_PATH);
  };

  if (forceReset || !fs.existsSync(EXCEL_FILE_PATH)) {
    await createCleanExcel();
  } else {
    // Check if existing Excel file has old pre-existing mock seed data or missing headers
    try {
      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.readFile(EXCEL_FILE_PATH);
      const sheet = workbook.getWorksheet("TuSi") || workbook.worksheets[0];
      let hasOldMock = false;
      sheet.eachRow((row, rowNumber) => {
        if (rowNumber > 1) {
          const idCell = row.getCell(1).value ? String(row.getCell(1).value) : "";
          if (idCell.startsWith("100000000000000") || idCell === "123456789012345678") {
            hasOldMock = true;
          }
        }
      });
      if (hasOldMock) {
        await createCleanExcel();
      }
    } catch {
      await createCleanExcel();
    }
  }
}

const EXCEL_COLUMNS = [
  "DiscordID",
  "Username",
  "Tên",
  "Cảnh giới",
  "EXP",
  "Linh thạch",
  "Linh căn",
  "HP",
  "Mana",
  "Ngày điểm danh",
  "Túi đồ",
  "Buff đột phá"
];

// Read all players from Excel safely
async function readPlayersFromExcel() {
  await ensureExcelExists();
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(EXCEL_FILE_PATH);
  const sheet = workbook.getWorksheet("TuSi") || workbook.worksheets[0];

  const players: any[] = [];
  const headerRow = sheet.getRow(1);
  const headersMap: { [key: string]: number } = {};

  headerRow.eachCell((cell, colNumber) => {
    if (cell.value) {
      headersMap[String(cell.value).trim()] = colNumber;
    }
  });

  sheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) return;

    const idCol = headersMap["DiscordID"] || 1;
    const discordIdVal = row.getCell(idCol).value;
    const discordId = discordIdVal !== null && discordIdVal !== undefined ? String(discordIdVal).trim() : "";
    if (!discordId) return;

    const player: any = {};
    EXCEL_COLUMNS.forEach((colName) => {
      const colIndex = headersMap[colName];
      if (colIndex) {
        const val = row.getCell(colIndex).value;
        player[colName] = val !== null && val !== undefined ? val : "";
      } else {
        player[colName] = "";
      }
    });

    player.DiscordID = String(player.DiscordID);
    player.Username = String(player.Username || "");
    player.Tên = String(player.Tên || player.Username || "");
    player["Cảnh giới"] = String(player["Cảnh giới"] || "Luyện Khí tầng 1");
    player.EXP = Number(player.EXP) || 0;
    player["Linh thạch"] = Number(player["Linh thạch"]) || 0;
    player["Linh căn"] = String(player["Linh căn"] || "Ngũ Hành Linh Căn");
    player.HP = Number(player.HP) || 100;
    player.Mana = Number(player.Mana) || 100;
    player["Ngày điểm danh"] = String(player["Ngày điểm danh"] || "");
    player["Túi đồ"] = String(player["Túi đồ"] || "{}");
    player["Buff đột phá"] = Number(player["Buff đột phá"]) || 0;

    players.push(player);
  });

  return players;
}

// Write/Update player to Excel with 1-based indexing for MS Excel compatibility
async function savePlayerToExcel(playerData: any) {
  await ensureExcelExists();
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(EXCEL_FILE_PATH);
  const sheet = workbook.getWorksheet("TuSi") || workbook.worksheets[0];

  const headerRow = sheet.getRow(1);
  const headersMap: { [key: string]: number } = {};

  headerRow.eachCell((cell, colNumber) => {
    if (cell.value) {
      headersMap[String(cell.value).trim()] = colNumber;
    }
  });

  // Ensure all required EXCEL_COLUMNS exist in header
  EXCEL_COLUMNS.forEach((colName) => {
    if (!headersMap[colName]) {
      const newColNum = Object.keys(headersMap).length + 1;
      headerRow.getCell(newColNum).value = colName;
      headersMap[colName] = newColNum;
    }
  });

  const discordIdCol = headersMap["DiscordID"];
  let targetRowNumber = -1;

  sheet.eachRow((row, rowNumber) => {
    if (rowNumber > 1) {
      const cellVal = row.getCell(discordIdCol).value;
      if (cellVal !== null && cellVal !== undefined && String(cellVal).trim() === String(playerData.DiscordID).trim()) {
        targetRowNumber = rowNumber;
      }
    }
  });

  if (targetRowNumber !== -1) {
    const row = sheet.getRow(targetRowNumber);
    Object.keys(playerData).forEach((key) => {
      const colIdx = headersMap[key];
      if (colIdx) {
        row.getCell(colIdx).value = playerData[key];
      }
    });
    row.commit();
  } else {
    // Add new row with proper col index mapping
    const rowValues: any[] = [];
    Object.keys(headersMap).forEach((colName) => {
      const colIdx = headersMap[colName];
      rowValues[colIdx] = playerData[colName] !== undefined ? playerData[colName] : "";
    });
    sheet.addRow(rowValues);
  }

  await workbook.xlsx.writeFile(EXCEL_FILE_PATH);
  return playerData;
}

// REST API Endpoints
app.get("/api/players", async (req, res) => {
  try {
    const players = await readPlayersFromExcel();
    res.json({ success: true, players });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get("/api/raw-files", (req, res) => {
  const filePaths = [
    "bot/main.py",
    "bot/config.py",
    "bot/logger.py",
    "bot/db_manager.py",
    "bot/excel_manager.py",
    "bot/import_onedrive.py",
    "bot/ai_handler.py",
    "bot/commands/info.py",
    "bot/commands/cultivation.py",
    "bot/commands/economy.py",
    "bot/commands/alchemy.py",
    "bot/commands/events.py",
    "bot/commands/admin.py",
    "bot/commands/help.py",
    "requirements.txt",
    "railway.json",
    "Procfile",
    ".env.example",
    "README.md",
    "server.ts"
  ];
  res.json({ success: true, files: filePaths });
});

app.get("/api/file-content", (req, res) => {
  try {
    const filePath = String(req.query.path || "");
    const safePath = path.normalize(filePath).replace(/^(\.\.[\/\\])+/, "");
    const fullPath = path.join(process.cwd(), safePath);

    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
      const content = fs.readFileSync(fullPath, "utf-8");
      res.json({ success: true, path: filePath, content });
    } else {
      res.status(404).json({ success: false, error: "File not found" });
    }
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get("/api/download/excel", (req, res) => {
  if (fs.existsSync(EXCEL_FILE_PATH)) {
    res.download(EXCEL_FILE_PATH, "data.xlsx");
  } else {
    res.status(404).send("File data.xlsx chưa được khởi tạo.");
  }
});

app.get("/api/download/db", (req, res) => {
  const dbPath = path.join(process.cwd(), "data", "cultivation.db");
  if (fs.existsSync(dbPath)) {
    res.download(dbPath, "cultivation.db");
  } else {
    res.status(404).send("File cultivation.db chưa được khởi tạo.");
  }
});

app.post("/api/players", async (req, res) => {
  try {
    const updated = await savePlayerToExcel(req.body);
    res.json({ success: true, player: updated });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Groq AI Chat Simulation
app.post("/api/simulate/chat", async (req, res) => {
  try {
    const { message, userDiscordId, userName } = req.body;
    const players = await readPlayersFromExcel();

    const apiKey = process.env.GROQ_API_KEY || process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return res.json({
        success: true,
        reply: `【Hệ Thống】\n\nKiểm tra dữ liệu ký chủ **${userName}**: "${message}".\n\nDữ liệu Tông Môn trong Excel: ${players.length} tu sĩ.\n\n(Lưu ý: Vui lòng cấu hình GROQ_API_KEY trong Secrets để Kích hoạt Hệ Thống AI hoàn chỉnh).`
      });
    }

    const groq = new Groq({ apiKey });

    const activeUser = players.find(p => String(p.DiscordID) === String(userDiscordId)) || {
      DiscordID: userDiscordId,
      Username: userName,
      Tên: userName,
      "Cảnh giới": "Luyện Khí tầng 1",
      EXP: 0,
      "Linh thạch": 100,
      "Linh căn": "Phàm Linh Căn"
    };

    const prompt = `
[DỮ LIỆU EXCEL TÔNG MÔN HIỆN TẠI]:
${JSON.stringify({ Nguoi_Hoi: activeUser, Danh_Sach_Excel: players }, null, 2)}

[CÂU HỎI CỦA KÝ CHỦ (${userName})]:
"${message}"
`;

    const systemInstruction = `
Bạn là 'Hệ Thống Tu Tiên' (System) hỗ trợ người chơi tu luyện trong thế giới huyền huyễn, tiên hiệp.
VAI TRÒ VÀ VĂN PHONG:
- Lập trường: Là một Hệ Thống vô cảm, khách quan nhưng lịch sự và hỗ trợ ký chủ hết lòng.
- Tuyệt đối KHÔNG xưng là AI, ChatGPT, OpenAI hay con người, không xưng 'Tôi', 'Lão phu' hay 'Đại Lão'.
- Tự xưng: 'Hệ Thống', 'Bổn Hệ Thống', hoặc 'Hệ Thống Tu Tiên'.
- Gọi người chơi: 'Ký chủ', 'Đạo hữu', 'Người tu luyện', hoặc 'Chủ nhân'.
- Định dạng bắt đầu: Mọi câu trả lời BẮT ĐẦU BẰNG "【Hệ Thống】" hoặc "【Đinh!】" (khi có phần thưởng, đột phá hoặc thành tựu).
- Văn phong: Ngắn gọn, rõ ràng, dạng thông báo hệ thống hoặc bảng trạng thái tu tiên.

QUY TẮC TRẢ LỜI:
1. Luôn dựa trên DỮ LIỆU EXCEL TÔNG MÔN.
2. Tuyệt đối KHÔNG tự bịa ra thông tin không có trong Excel.
3. Nếu không có dữ liệu về người chơi trong Excel, trả lời chính xác:
【Hệ Thống】

Không tìm thấy thông tin của ký chủ.
4. Nếu câu hỏi ngoài phạm vi dữ liệu Excel:
【Hệ Thống】

Không có dữ liệu liên quan trong cơ sở dữ liệu của Hệ Thống.
`;

    const response = await groq.chat.completions.create({
      messages: [
        { role: "system", content: systemInstruction },
        { role: "user", content: prompt }
      ],
      model: "llama-3.3-70b-versatile",
      temperature: 0.2
    });

    res.json({ success: true, reply: response.choices[0]?.message?.content || "【Hệ Thống】\n\nĐang quét dữ liệu tu vi..." });
  } catch (error: any) {
    console.error("Groq Error:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Downloadable ZIP of full Python Discord Bot Project
app.get("/api/export-zip", async (req, res) => {
  try {
    const zip = new JSZip();

    const rootFiles = [
      "requirements.txt",
      "railway.json",
      "Procfile",
      ".env.example",
      ".gitignore",
      "README.md",
      "server.ts"
    ];

    for (const file of rootFiles) {
      const fullPath = path.join(process.cwd(), file);
      if (fs.existsSync(fullPath)) {
        zip.file(file, fs.readFileSync(fullPath, "utf-8"));
      }
    }

    const botDir = path.join(process.cwd(), "bot");
    if (fs.existsSync(botDir)) {
      const readDirRecursive = (dirPath: string, zipPrefix: string) => {
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });
        for (const entry of entries) {
          const fullP = path.join(dirPath, entry.name);
          const zipP = path.join(zipPrefix, entry.name);
          if (entry.isDirectory()) {
            readDirRecursive(fullP, zipP);
          } else if (entry.isFile()) {
            zip.file(zipP, fs.readFileSync(fullP));
          }
        }
      };
      readDirRecursive(botDir, "bot");
    }

    if (fs.existsSync(EXCEL_FILE_PATH)) {
      const excelBuf = fs.readFileSync(EXCEL_FILE_PATH);
      zip.file("data/data.xlsx", excelBuf);
    }

    const dbPath = path.join(process.cwd(), "data", "cultivation.db");
    if (fs.existsSync(dbPath)) {
      const dbBuf = fs.readFileSync(dbPath);
      zip.file("data/cultivation.db", dbBuf);
    }

    const zipBuffer = await zip.generateAsync({ type: "nodebuffer" });
    res.setHeader("Content-Type", "application/zip");
    res.setHeader("Content-Disposition", "attachment; filename=TongMonDiscordBot_Moi.zip");
    res.send(zipBuffer);
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

async function startServer() {
  await ensureExcelExists();

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
