"""
ログ末尾抽出モジュール

ログファイルの末尾N行を効率的に抽出する機能を提供します。
"""

import logging
import os

logger = logging.getLogger(__name__)


def extract_log_tail(log_path: str, lines: int = 10, max_line_length: int = 500) -> list[str]:
    """
    ログファイルの末尾N行を抽出
    
    大きなファイルでも高速に動作するよう、ファイルの末尾から読み込みます。
    
    Args:
        log_path: ログファイルのパス
        lines: 抽出する行数（デフォルト: 10）
        max_line_length: 1行あたりの最大文字数（デフォルト: 500）
    
    Returns:
        末尾N行のリスト（古い順）
        
    Raises:
        FileNotFoundError: ファイルが存在しない
        PermissionError: 読み込み権限がない
    """
    if lines <= 0:
        logger.debug("lines <= 0, returning empty list")
        return []
    
    if not os.path.exists(log_path):
        logger.warning("Log file not found: %s", log_path)
        raise FileNotFoundError(f"Log file not found: {log_path}")
    
    try:
        with open(log_path, 'rb') as f:
            # ファイルサイズを取得
            f.seek(0, 2)  # 末尾に移動
            file_size = f.tell()
            
            if file_size == 0:
                logger.info("Log file is empty: %s", log_path)
                return []
            
            # 末尾から読み込む
            buffer_size = 8192  # 8KB
            max_read_size = 102400  # 100KB（安全装置）
            read_size = 0
            lines_found = []
            buffer = b''
            
            # 末尾から少しずつ読み込む
            position = file_size
            while len(lines_found) < lines and read_size < max_read_size:
                # 読み込むサイズを決定
                chunk_size = min(buffer_size, position)
                if chunk_size == 0:
                    break
                
                # 読み込み位置を移動
                position -= chunk_size
                f.seek(position)
                
                # データを読み込む
                chunk = f.read(chunk_size)
                read_size += chunk_size
                
                # バッファに追加（逆順）
                buffer = chunk + buffer
                
                # 改行で分割
                lines_in_buffer = buffer.split(b'\n')
                
                # 最後の要素は不完全な可能性があるので保持
                buffer = lines_in_buffer[0]
                
                # 完全な行を追加（逆順）
                for line in reversed(lines_in_buffer[1:]):
                    if len(lines_found) >= lines:
                        break
                    
                    try:
                        decoded_line = line.decode('utf-8', errors='replace').rstrip()
                        
                        # 空行はスキップ
                        if not decoded_line:
                            continue
                        
                        # 長い行を切り詰める
                        if len(decoded_line) > max_line_length:
                            decoded_line = decoded_line[:max_line_length] + " ... (truncated)"
                        
                        lines_found.append(decoded_line)
                    except Exception as e:
                        logger.warning("Failed to decode line: %s", e)
                        continue
            
            # 最初のバッファも処理
            if len(lines_found) < lines and buffer:
                try:
                    decoded_line = buffer.decode('utf-8', errors='replace').rstrip()
                    
                    # 空行はスキップ
                    if decoded_line:
                        # 長い行を切り詰める
                        if len(decoded_line) > max_line_length:
                            decoded_line = decoded_line[:max_line_length] + " ... (truncated)"
                        
                        lines_found.append(decoded_line)
                except Exception as e:
                    logger.warning("Failed to decode line: %s", e)
            
            # 古い順に並べ替え
            lines_found.reverse()
            
            logger.debug("Extracted %d lines from %s", len(lines_found), log_path)
            return lines_found
            
    except PermissionError:
        logger.warning("Permission denied: %s", log_path)
        raise
    except Exception as e:
        logger.error("Failed to extract log tail: %s", e, exc_info=True)
        raise
