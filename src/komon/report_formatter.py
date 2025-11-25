"""
レポートフォーマッターモジュール

週次健全性レポートのメッセージフォーマット機能を提供します。
"""


def format_weekly_report(data: dict) -> str:
    """
    週次レポートデータを人間が読みやすいメッセージにフォーマットします。
    
    Args:
        data: collect_weekly_data() からのレポートデータ
        
    Returns:
        str: フォーマット済みレポートメッセージ
    """
    period = data.get('period', {})
    resources = data.get('resources', {})
    alerts = data.get('alerts', [])
    
    # ヘッダー
    lines = [
        f"📊 週次健全性レポート ({period.get('start', '')} 〜 {period.get('end', '')})",
        "",
        "【リソース状況】"
    ]
    
    # リソース状況
    resource_names = {
        'cpu': 'CPU使用率',
        'mem': 'メモリ使用率',
        'disk': 'ディスク使用率'
    }
    
    for resource_key in ['cpu', 'mem', 'disk']:
        if resource_key in resources:
            resource_data = resources[resource_key]
            resource_name = resource_names.get(resource_key, resource_key.upper())
            lines.append(format_resource_status(
                resource_name,
                resource_data.get('current', 0),
                resource_data.get('change', 0)
            ))
    
    # 警戒情報
    lines.append("")
    lines.append("【今週の警戒情報】")
    if alerts:
        alert_summary = format_alert_summary(alerts)
        lines.append(alert_summary)
    else:
        lines.append("- なし")
    
    # トレンド
    lines.append("")
    lines.append("【トレンド】")
    for resource_key in ['cpu', 'mem', 'disk']:
        if resource_key in resources:
            resource_data = resources[resource_key]
            resource_name = resource_names.get(resource_key, resource_key.upper())
            trend = resource_data.get('trend', 'stable')
            trend_indicator = format_trend_indicator(trend)
            lines.append(f"{trend_indicator} {resource_name}: {get_trend_text(trend)}")
    
    # ディスク使用量の予測
    disk_prediction = data.get('disk_prediction')
    if disk_prediction:
        prediction_section = format_disk_prediction(disk_prediction)
        if prediction_section:
            lines.append("")
            lines.append(prediction_section)
    
    # フッター
    lines.append("")
    lines.append("異常がなくても、定期的に確認しておくと安心ですね 👀")
    
    return "\n".join(lines)


def format_resource_status(resource: str, current: float, change: float) -> str:
    """
    個別リソース状態行をフォーマットします。
    
    Args:
        resource: リソース名（例: 'CPU使用率'）
        current: 現在の値（%）
        change: 変化率（%）
        
    Returns:
        str: フォーマット済み文字列（例: 'CPU使用率: 45.2% (先週比 +2.1%)'）
    """
    if change >= 0:
        change_str = f"+{change:.1f}%"
    else:
        change_str = f"{change:.1f}%"
    
    return f"{resource}: {current:.1f}% (先週比 {change_str})"


def format_trend_indicator(trend: str) -> str:
    """
    トレンドを視覚的インジケーターに変換します。
    
    Args:
        trend: 'stable', 'increasing', または 'decreasing'
        
    Returns:
        str: 絵文字インジケーター
    """
    indicators = {
        'stable': '✅',
        'increasing': '⚠️',
        'decreasing': '📉'
    }
    return indicators.get(trend, '❓')


def get_trend_text(trend: str) -> str:
    """
    トレンドを日本語テキストに変換します。
    
    Args:
        trend: 'stable', 'increasing', または 'decreasing'
        
    Returns:
        str: 日本語テキスト
    """
    texts = {
        'stable': '安定',
        'increasing': '緩やかに増加傾向',
        'decreasing': '減少傾向'
    }
    return texts.get(trend, '不明')


def format_alert_summary(alerts: list) -> str:
    """
    警戒情報のサマリーをフォーマットします。
    
    Args:
        alerts: 警戒情報のリスト
        
    Returns:
        str: フォーマット済みサマリー
    """
    if not alerts:
        return "- なし"
    
    # 最大5件まで表示
    display_alerts = alerts[:5]
    
    lines = []
    for alert in display_alerts:
        timestamp = alert.get('timestamp', '')
        message = alert.get('message', '')
        
        # メッセージから最初の行のみ抽出（複数行の場合）
        first_line = message.split('\n')[0] if message else ''
        
        # 長すぎる場合は省略
        if len(first_line) > 60:
            first_line = first_line[:57] + '...'
        
        lines.append(f"- {timestamp} - {first_line}")
    
    # 5件以上ある場合は省略表示
    if len(alerts) > 5:
        lines.append(f"- ...他 {len(alerts) - 5} 件")
    
    return "\n".join(lines)



def format_disk_prediction(disk_prediction: dict) -> str:
    """
    ディスク使用量の予測をフォーマットします。
    
    Args:
        disk_prediction: {
            'prediction': {...},
            'rapid_change': {...}
        }
        
    Returns:
        str: フォーマット済み予測セクション
    """
    if not disk_prediction:
        return ""
    
    from komon.disk_predictor import format_prediction_message
    
    prediction = disk_prediction.get('prediction', {})
    rapid_change = disk_prediction.get('rapid_change', {})
    
    # 予測メッセージを生成
    message = format_prediction_message(prediction, rapid_change)
    
    # 警告がある場合は目立つ形式で表示
    if rapid_change.get('is_rapid') or prediction.get('days_to_90') is not None:
        return f"【⚠️ ディスク使用量の予測】\n{message}"
    else:
        # 安全な場合は簡潔な形式
        return f"【📊 ディスク使用量の予測】\n{message}"
