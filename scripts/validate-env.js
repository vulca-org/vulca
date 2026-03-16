#!/usr/bin/env node
/**
 * Environment validation script — ensures local env matches GitHub Actions CI.
 * Validates Node.js, Python versions, npm config, and key dependencies.
 */

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

// GitHub Actions环境标准配置
const EXPECTED_VERSIONS = {
  node: '20.19.4',
  npm: '10.0.0',
  python: '3.10'
};

const REQUIRED_FILES = [
  '.nvmrc',
  '.python-version',
  '.npmrc',
  'wenxin-moyun/package.json',
  'wenxin-backend/requirements.txt'
];

console.log('🔍 验证环境配置与GitHub Actions CI的一致性...\n');

let hasErrors = false;

/**
 * 执行命令并返回输出
 */
function execCommand(command) {
  try {
    return execSync(command, { encoding: 'utf8', cwd: projectRoot }).trim();
  } catch (error) {
    return null;
  }
}

/**
 * 检查版本是否匹配
 */
function checkVersion(actual, expected, name) {
  if (!actual) {
    console.log(`❌ ${name}: 未安装`);
    hasErrors = true;
    return false;
  }
  
  // 对于npm，检查是否大于等于要求的版本
  if (name === 'npm') {
    const actualMajor = parseInt(actual.split('.')[0]);
    const expectedMajor = parseInt(expected.split('.')[0]);
    
    if (actualMajor >= expectedMajor) {
      console.log(`✅ ${name}: ${actual} (满足要求 ≥${expected})`);
      return true;
    } else {
      console.log(`⚠️  ${name}: ${actual} (需要 ≥${expected})`);
      hasErrors = true;
      return false;
    }
  } else {
    // 对于Node.js和Python，检查主版本号和次版本号
    const actualVersion = actual.split('.').slice(0, 2).join('.');
    const expectedVersion = expected.split('.').slice(0, 2).join('.');
    
    if (actualVersion === expectedVersion) {
      console.log(`✅ ${name}: ${actual} (匹配期望 ${expected})`);
      return true;
    } else {
      console.log(`⚠️  ${name}: ${actual} (期望 ${expected})`);
      hasErrors = true;
      return false;
    }
  }
}

/**
 * 检查文件是否存在
 */
function checkFile(filePath) {
  const fullPath = join(projectRoot, filePath);
  const exists = existsSync(fullPath);
  
  if (exists) {
    console.log(`✅ 配置文件: ${filePath}`);
    return true;
  } else {
    console.log(`❌ 配置文件缺失: ${filePath}`);
    hasErrors = true;
    return false;
  }
}

// 1. 检查Node.js版本
console.log('📦 检查Node.js环境:');
const nodeVersion = execCommand('node --version')?.replace('v', '');
checkVersion(nodeVersion, EXPECTED_VERSIONS.node, 'Node.js');

// 2. 检查npm版本
const npmVersion = execCommand('npm --version');
checkVersion(npmVersion, EXPECTED_VERSIONS.npm, 'npm');

// 3. 检查Python版本
console.log('\n🐍 检查Python环境:');
const pythonVersion = execCommand('python --version')?.replace('Python ', '') || 
                     execCommand('python3 --version')?.replace('Python ', '');
checkVersion(pythonVersion, EXPECTED_VERSIONS.python, 'Python');

// 4. 检查配置文件
console.log('\n📁 检查配置文件:');
REQUIRED_FILES.forEach(checkFile);

// 5. 验证.nvmrc内容
console.log('\n🔧 验证版本锁定文件内容:');
try {
  const nvmrcPath = join(projectRoot, '.nvmrc');
  if (existsSync(nvmrcPath)) {
    const nvmrcContent = readFileSync(nvmrcPath, 'utf8').trim();
    if (nvmrcContent === EXPECTED_VERSIONS.node) {
      console.log(`✅ .nvmrc: ${nvmrcContent}`);
    } else {
      console.log(`❌ .nvmrc: ${nvmrcContent} (期望 ${EXPECTED_VERSIONS.node})`);
      hasErrors = true;
    }
  }
} catch (error) {
  console.log(`❌ 无法读取.nvmrc: ${error.message}`);
  hasErrors = true;
}

// 6. 验证.python-version内容
try {
  const pythonVersionPath = join(projectRoot, '.python-version');
  if (existsSync(pythonVersionPath)) {
    const pythonVersionContent = readFileSync(pythonVersionPath, 'utf8').trim();
    if (pythonVersionContent === EXPECTED_VERSIONS.python) {
      console.log(`✅ .python-version: ${pythonVersionContent}`);
    } else {
      console.log(`❌ .python-version: ${pythonVersionContent} (期望 ${EXPECTED_VERSIONS.python})`);
      hasErrors = true;
    }
  }
} catch (error) {
  console.log(`❌ 无法读取.python-version: ${error.message}`);
  hasErrors = true;
}

// 7. 验证package.json engines字段
console.log('\n⚙️  验证package.json engines配置:');
try {
  const packageJsonPath = join(projectRoot, 'wenxin-moyun/package.json');
  if (existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'));
    if (packageJson.engines && packageJson.engines.node) {
      console.log(`✅ package.json engines.node: ${packageJson.engines.node}`);
    } else {
      console.log(`❌ package.json 缺少 engines.node 字段`);
      hasErrors = true;
    }
  }
} catch (error) {
  console.log(`❌ 无法读取package.json: ${error.message}`);
  hasErrors = true;
}

// 8. 检查npm配置
console.log('\n📋 检查npm配置:');
const npmConfig = execCommand('npm config list');
if (npmConfig) {
  if (npmConfig.includes('legacy-peer-deps = true')) {
    console.log(`✅ npm配置: legacy-peer-deps = true`);
  } else {
    console.log(`⚠️  npm配置: legacy-peer-deps 未设置为 true`);
    console.log(`   建议运行: npm config set legacy-peer-deps true`);
  }
}

// 9. 检查Playwright安装
console.log('\n🎭 检查Playwright配置:');
const playwrightVersion = execCommand('npx playwright --version');
if (playwrightVersion) {
  console.log(`✅ Playwright: ${playwrightVersion}`);
} else {
  console.log(`❌ Playwright 未安装或配置错误`);
  hasErrors = true;
}

// 总结
console.log('\n' + '='.repeat(60));
if (hasErrors) {
  console.log('❌ 环境验证失败！存在以下问题需要修复:');
  console.log('\n修复建议:');
  console.log('1. 使用nvm安装正确的Node.js版本: nvm install 20.19.4 && nvm use 20.19.4');
  console.log('2. 更新npm到最新版本: npm install -g npm@latest');
  console.log('3. 检查Python版本: python --version 或 python3 --version');
  console.log('4. 运行 npm install 重新安装依赖');
  console.log('5. 运行 npx playwright install 安装浏览器');
  process.exit(1);
} else {
  console.log('✅ 环境验证通过！本地环境与GitHub Actions CI保持一致。');
  process.exit(0);
}