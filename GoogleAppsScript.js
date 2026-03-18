// Google Apps Script - 部署为 Web App
// 1. 打开 https://script.google.com
// 2. 新建项目
// 3. 粘贴此代码
// 4. 部署 > 新建部署 > Web App
// 5. 执行身份：本人，访问权限：任何人
// 6. 把部署后的 URL 复制到下面

function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({error: 'Sheet not found'}))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  const data = JSON.parse(e.postData.contents);
  const email = data.email;
  const timestamp = new Date();
  
  sheet.appendRow([timestamp, email]);
  
  return ContentService.createTextOutput(JSON.stringify({success: true}))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({status: 'ok'}))
    .setMimeType(ContentService.MimeType.JSON);
}
