/**
 * 多平台一键发布脚本
 * 支持: 微信、知乎、掘金、CSDN、简书、头条、SegmentFault
 * 
 * 使用方法:
 *   node multi_publish.js --article output/article.md --platforms "1,3,4"
 *   node multi_publish.js --article output/article.md --all
 */

const mulitArticlePublisher = require('mulit-article-publisher');
const fs = require('fs');
const path = require('path');

// 平台映射
const PLATFORMS = {
  1: '微信公众号',
  2: '今日头条',
  3: '知乎',
  4: '掘金',
  5: 'SegmentFault',
  6: '简书',
  7: 'CSDN'
};

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    articlePath: '',
    allPlatform: false,
    platforms: []
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--article':
        options.articlePath = args[++i];
        break;
      case '--platforms':
        options.platforms = args[++i].split(',').map(n => parseInt(n.trim()));
        break;
      case '--all':
        options.allPlatform = true;
        break;
      case '--help':
      case '-h':
        printHelp();
        process.exit(0);
    }
  }

  return options;
}

function printHelp() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║            多平台一键发布工具 v1.0                          ║
╠════════════════════════════════════════════════════════════╣
║  使用方法:                                                  ║
║    node multi_publish.js --article <文章路径> [选项]        ║
║                                                             ║
║  选项:                                                      ║
║    --article <path>   文章路径 (.md 文件)                   ║
║    --platforms <list> 指定平台编号，逗号分隔                ║
║    --all              发布到所有平台                        ║
║    --help, -h         显示帮助                              ║
║                                                             ║
║  平台编号:                                                  ║
║    1 - 微信公众号 (存入素材库)                              ║
║    2 - 今日头条                                             ║
║    3 - 知乎                                                 ║
║    4 - 掘金                                                 ║
║    5 - SegmentFault                                         ║
║    6 - 简书                                                 ║
║    7 - CSDN                                                 ║
║                                                             ║
║  示例:                                                      ║
║    node multi_publish.js --article output/article.md --all ║
║    node multi_publish.js --article article.md -p "1,3,4"   ║
╚════════════════════════════════════════════════════════════╝
  `);
}

async function main() {
  const options = parseArgs();

  // 验证参数
  if (!options.articlePath) {
    console.error('❌ 错误: 请指定文章路径 (--article)');
    printHelp();
    process.exit(1);
  }

  if (!fs.existsSync(options.articlePath)) {
    console.error(`❌ 错误: 文件不存在 ${options.articlePath}`);
    process.exit(1);
  }

  if (!options.allPlatform && options.platforms.length === 0) {
    console.error('❌ 错误: 请指定发布平台 (--platforms 或 --all)');
    printHelp();
    process.exit(1);
  }

  // 显示发布信息
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║            多平台一键发布                                  ║');
  console.log('╠════════════════════════════════════════════════════════════╣\n');
  console.log(`📄 文章: ${options.articlePath}`);
  
  if (options.allPlatform) {
    console.log('📤 发布平台: 全部 (7个)');
    Object.entries(PLATFORMS).forEach(([id, name]) => {
      console.log(`   ${id}. ${name}`);
    });
  } else {
    console.log('📤 发布平台:');
    options.platforms.forEach(id => {
      console.log(`   ${id}. ${PLATFORMS[id] || '未知'}`);
    });
  }

  console.log('\n⚠️  注意: 请确保已在 Chrome 浏览器中登录各平台账号\n');
  console.log('🚀 开始发布...\n');

  try {
    // 调用发布函数
    await mulitArticlePublisher({
      articlePath: path.resolve(options.articlePath),
      allPlatfom: options.allPlatform,
      platform: options.platforms
    });

    console.log('\n✅ 发布完成！\n');
  } catch (error) {
    console.error('\n❌ 发布失败:', error.message);
    console.error('\n可能的原因:');
    console.error('  1. 未在 Chrome 浏览器中登录平台账号');
    console.error('  2. Chrome 浏览器未安装或路径不正确');
    console.error('  3. 文章格式不符合平台要求');
    process.exit(1);
  }
}

main();
