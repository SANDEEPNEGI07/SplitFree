// Simple validation script to check our imports
const fs = require('fs');
const path = require('path');

console.log('Checking frontend files...');

// Check if key files exist
const filesToCheck = [
  'src/App.jsx',
  'src/components/UI/UserSearch.jsx',
  'src/pages/GroupDetails.jsx',
  'src/services/api.js',
  'src/services/groups.js',
  'src/services/expenses.js',
  'src/hooks/useApi.js'
];

let allFilesExist = true;

filesToCheck.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.log(`❌ ${file} missing`);
    allFilesExist = false;
  }
});

if (allFilesExist) {
  console.log('\n✅ All required files exist!');
} else {
  console.log('\n❌ Some files are missing');
  process.exit(1);
}

console.log('\nValidation complete!');