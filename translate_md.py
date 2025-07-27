from deep_translator import GoogleTranslator
import sys
import logging
import os
import time

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)

def translate_markdown(input_path, output_path):
    # 确保输出路径在 translation 文件夹下
    output_dir = os.path.join(os.getcwd(), "translation")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(output_path))
    
    logger.info(f"开始翻译: {input_path} → {output_path}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        logger.debug(f"成功读取输入文件，共 {len(lines)} 行")
    except Exception as e:
        logger.error(f"读取输入文件失败: {str(e)}")
        return

    translated_lines = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        try:
            line_num = i + 1
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                translated_lines.append(line)
                logger.debug(f"行 {line_num}: 代码块标记，{'进入' if in_code_block else '退出'}代码块")
                continue
                
            if in_code_block:
                translated_lines.append(line)
                logger.debug(f"行 {line_num}: 代码块内容，不翻译")
                continue
                
            if line.strip() == "":
                translated_lines.append(line)
                logger.debug(f"行 {line_num}: 空行，不翻译")
                continue
                
            logger.debug(f"行 {line_num}: 翻译内容: {line.strip()}")
            
            # 添加重试逻辑
            max_retries = 3
            for retry in range(max_retries):
                try:
                    translated = GoogleTranslator(source='auto', target='en').translate(line)
                    
                    # 处理翻译结果为None的情况
                    if translated is None:
                        logger.warning(f"行 {line_num}: 翻译结果为None，保留原文")
                        translated = line.strip()
                    
                    translated_lines.append(translated + "\n")
                    logger.debug(f"行 {line_num}: 翻译结果: {translated.strip()}")
                    break
                except Exception as e:
                    if retry < max_retries - 1:
                        wait_time = (retry + 1) * 2  # 指数退避
                        logger.warning(f"翻译失败，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"翻译第 {i+1} 行时出错: {str(e)}")
            translated_lines.append(line)  # 翻译失败时保留原文

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
        logger.info(f"翻译完成，已保存到 {output_path}")
    except Exception as e:
        logger.error(f"写入输出文件失败: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("用法: python translate_md.py <输入文件> <输出文件>")
        sys.exit(1)
    
    translate_markdown(sys.argv[1], sys.argv[2])