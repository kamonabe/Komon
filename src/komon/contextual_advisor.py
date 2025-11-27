"""
コンテキストに応じた具体的アドバイスを生成するモジュール

プロセス情報の取得、パターンマッチング、提案生成を行う。
"""

import logging
import psutil
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

# デフォルトパターン定義
DEFAULT_PATTERNS = {
    "node": {
        "keywords": ["node", "npm", "yarn", "webpack"],
        "advice": "開発サーバーが起動しっぱなしかも？不要なら停止してみてください",
        "detailed_advice": "停止方法: kill {pid} または Ctrl+C"
    },
    "docker": {
        "keywords": ["docker", "containerd"],
        "advice": "不要なコンテナが残っているかも？`docker ps` で確認してみてください",
        "detailed_advice": "確認方法: docker ps\n停止方法: docker stop <container_id>"
    },
    "python": {
        "keywords": ["python", "python3"],
        "advice": "学習プロセスや長時間スクリプトが動いているかも？確認してみてください",
        "detailed_advice": "確認方法: ps aux | grep python"
    },
    "java": {
        "keywords": ["java", "javac"],
        "advice": "Javaアプリケーションが動いているかも？不要なら停止してみてください",
        "detailed_advice": "確認方法: jps -l"
    },
    "database": {
        "keywords": ["mysql", "postgres", "mongod", "redis"],
        "advice": "データベースが高負荷かも？クエリやインデックスを確認してみてください",
        "detailed_advice": "確認方法: データベースのスロークエリログを確認"
    }
}


def get_contextual_advice(
    metric_type: str,
    config: Dict[str, Any],
    advice_level: str = "normal"
) -> Dict[str, Any]:
    """
    コンテキストに応じた具体的アドバイスを生成
    
    Args:
        metric_type: メトリクスタイプ（"cpu" または "memory"）
        config: 設定ファイルの内容
        advice_level: 詳細度（"minimal", "normal", "detailed"）
    
    Returns:
        {
            "top_processes": [...],
            "formatted_message": "..."
        }
    
    Raises:
        ValueError: metric_typeが不正な場合
    """
    if metric_type not in ["cpu", "memory"]:
        raise ValueError(f"Invalid metric_type: {metric_type}")
    
    # 設定から値を取得
    contextual_config = config.get("contextual_advice", {})
    top_count = contextual_config.get("top_processes_count", 3)
    patterns = contextual_config.get("patterns", DEFAULT_PATTERNS)
    
    # 上位プロセスを取得
    processes = _get_top_processes(metric_type, top_count)
    
    # 各プロセスにパターンマッチングを適用
    for process in processes:
        pattern_name, advice = _match_pattern(process["name"], patterns)
        process["pattern"] = pattern_name
        process["advice"] = advice
        
        # detailed_adviceも取得
        if pattern_name in patterns:
            process["detailed_advice"] = patterns[pattern_name].get("detailed_advice", "")
    
    # メッセージを整形
    formatted_message = _format_advice(processes, advice_level)
    
    return {
        "top_processes": processes,
        "formatted_message": formatted_message
    }


def _get_top_processes(metric_type: str, count: int = 3) -> List[Dict[str, Any]]:
    """
    上位プロセスを取得
    
    Args:
        metric_type: "cpu" または "memory"
        count: 取得件数
    
    Returns:
        プロセス情報のリスト
    """
    processes = []
    
    try:
        # 第1段階: 全プロセスの情報を高速に取得（interval=0）
        for proc in psutil.process_iter(['name', 'pid', 'memory_percent', 'cmdline']):
            try:
                info = proc.info
                
                # CPU使用率は一旦0で取得（高速化のため）
                memory_percent = info.get('memory_percent', 0.0)
                
                # コマンドラインを文字列に変換
                cmdline = info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                processes.append({
                    "name": info.get('name', 'unknown'),
                    "pid": info.get('pid', 0),
                    "proc": proc,  # 後で再測定するために保持
                    "cpu_percent": 0.0,  # 後で更新
                    "memory_percent": memory_percent,
                    "cmdline": cmdline_str
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                logger.debug("Skipping process during initial scan")
                continue
            except Exception as e:
                logger.warning("Failed to get process info: %s", e)
                continue
    
    except Exception as e:
        logger.error("Failed to iterate processes: %s", e)
        return []
    
    # 第2段階: メトリクスタイプに応じて処理
    if metric_type == "cpu":
        # CPU使用率の場合、上位候補を多めに取得してから再測定
        # メモリ使用率でソートして上位20件を取得（CPU使用率が高いプロセスはメモリも使う傾向）
        processes.sort(key=lambda p: p["memory_percent"], reverse=True)
        top_candidates = processes[:min(20, len(processes))]
        
        # 上位候補のCPU使用率を測定
        for p in top_candidates:
            try:
                p["cpu_percent"] = p["proc"].cpu_percent(interval=0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                p["cpu_percent"] = 0.0
            except Exception as e:
                logger.warning("Failed to get CPU percent for process %s: %s", p.get("pid"), e)
                p["cpu_percent"] = 0.0
            # procオブジェクトは不要なので削除
            if "proc" in p:
                del p["proc"]
        
        # CPU使用率で再ソート
        top_candidates.sort(key=lambda p: p["cpu_percent"], reverse=True)
        return top_candidates[:count]
    
    else:  # memory
        # メモリ使用率の場合、既にソート済み
        processes.sort(key=lambda p: p["memory_percent"], reverse=True)
        top_processes = processes[:count]
        
        # procオブジェクトを削除
        for p in top_processes:
            if "proc" in p:
                del p["proc"]
        
        return top_processes


def _match_pattern(process_name: str, patterns: Dict[str, Any]) -> Tuple[str, str]:
    """
    プロセス名からパターンをマッチング
    
    Args:
        process_name: プロセス名
        patterns: パターン定義
    
    Returns:
        (パターン名, アドバイステキスト)
    """
    if not process_name:
        return ("unknown", "このプロセスが高負荷です。必要なければ停止を検討してください")
    
    # 小文字に変換
    process_name_lower = process_name.lower()
    
    # パターンを順番に走査
    for pattern_name, pattern_config in patterns.items():
        keywords = pattern_config.get("keywords", [])
        
        # キーワードと部分一致チェック
        for keyword in keywords:
            if keyword.lower() in process_name_lower:
                advice = pattern_config.get("advice", "このプロセスが高負荷です")
                return (pattern_name, advice)
    
    # マッチしない場合はデフォルト
    return ("unknown", "このプロセスが高負荷です。必要なければ停止を検討してください")


def _format_advice(processes: List[Dict[str, Any]], advice_level: str) -> str:
    """
    プロセス情報を整形してメッセージを生成
    
    Args:
        processes: プロセス情報のリスト
        advice_level: 詳細度（"minimal", "normal", "detailed"）
    
    Returns:
        整形されたメッセージ
    """
    if not processes:
        return "（プロセス情報を取得できませんでした）"
    
    # 詳細度の検証
    if advice_level not in ["minimal", "normal", "detailed"]:
        logger.warning("Invalid advice_level: %s, using 'normal'", advice_level)
        advice_level = "normal"
    
    lines = ["\n上位プロセス:"]
    
    for process in processes:
        name = process.get("name", "unknown")
        pid = process.get("pid", 0)
        cpu = process.get("cpu_percent", 0.0)
        mem = process.get("memory_percent", 0.0)
        advice = process.get("advice", "")
        cmdline = process.get("cmdline", "")
        detailed_advice = process.get("detailed_advice", "")
        
        if advice_level == "minimal":
            # プロセス名、PID、使用率のみ
            lines.append(f"- {name} (PID {pid}): CPU {cpu:.1f}%, メモリ {mem:.1f}%")
        
        elif advice_level == "normal":
            # プロセス名、PID、使用率、簡潔な提案
            lines.append(f"- {name} (PID {pid}): CPU {cpu:.1f}%, メモリ {mem:.1f}%")
            if advice:
                lines.append(f"  → {advice}")
        
        else:  # detailed
            # プロセス名、PID、使用率、コマンドライン、詳細な提案
            lines.append(f"- {name} (PID {pid}): CPU {cpu:.1f}%, メモリ {mem:.1f}%")
            if cmdline:
                # コマンドラインが長い場合は省略
                if len(cmdline) > 80:
                    cmdline = cmdline[:77] + "..."
                lines.append(f"  コマンド: {cmdline}")
            if advice:
                lines.append(f"  → {advice}")
            if detailed_advice:
                # {pid}を実際のPIDに置換
                detailed_advice = detailed_advice.replace("{pid}", str(pid))
                lines.append(f"  {detailed_advice}")
    
    return "\n".join(lines)
