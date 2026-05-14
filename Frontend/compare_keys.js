
const fs = require('fs');
const content = fs.readFileSync('src/contexts/LanguageContext.tsx', 'utf8');

const enMatch = content.match(/en: \{([\s\S]*?)\},/);
const urMatch = content.match(/ur: \{([\s\S]*?)\},/);

if (!enMatch || !urMatch) {
    console.log("Could not find en or ur objects");
    console.log("enMatch:", !!enMatch);
    console.log("urMatch:", !!urMatch);
    process.exit(1);
}

const getKeys = (text) => {
    const keys = [];
    const lines = text.split('\n');
    lines.forEach(line => {
        const match = line.match(/^\s*(\w+):/);
        if (match) keys.push(match[1]);
    });
    return keys;
};

const enKeys = getKeys(enMatch[1]);
const urKeys = getKeys(urMatch[1]);

const missingInEn = urKeys.filter(k => !enKeys.includes(k));
const missingInUr = enKeys.filter(k => !urKeys.includes(k));

console.log("Missing in EN:", missingInEn);
console.log("Missing in UR:", missingInUr);
