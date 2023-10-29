const fs = require('fs').promises;
const path = require('path');

async function readTextFilesFromFolder(folderPath) {
  const fileNames = await fs.readdir(folderPath);
  const textFiles = fileNames.filter((file) => path.extname(file) === '.txt');
  const output = [];

  for (const file of textFiles) {
    const text = await fs.readFile(path.join(folderPath, file), 'utf-8');
    output.push({ filename: file, content: text });
  }
  
  console.log(JSON.stringify(output));
}
