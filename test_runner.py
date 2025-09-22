"""
テストランナー
Comprehensive test runner for the Phase 5 implementation
"""
import sys
import subprocess
import time


def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n{'='*60}")
    print(f"実行中: {description}")
    print(f"コマンド: {command}")
    print('='*60)
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"実行時間: {end_time - start_time:.2f}秒")
    print(f"終了コード: {result.returncode}")
    
    if result.stdout:
        print("\n標準出力:")
        print(result.stdout)
    
    if result.stderr:
        print("\n標準エラー出力:")
        print(result.stderr)
    
    return result.returncode == 0


def main():
    """メインテスト実行関数"""
    print("フェーズ5: テスト・品質向上 - 包括的テスト実行")
    print("=" * 60)
    
    tests = [
        ("python -m pytest test_game_states.py -v", "ユニットテスト: 状態遷移"),
        ("python -m pytest test_stats_aggregation.py -v", "ユニットテスト: stats 集計"),
        ("python -m pytest test_remaining_time.py -v", "残り時間計算テスト"),
        ("python -m pytest test_integration_workflow.py -v", "統合テスト: start→pause→resume→complete→stats更新"),
        ("python -m pytest test_error_responses.py -v", "エラーレスポンス統一テスト"),
        ("python -m pytest test_*.py --tb=short", "全テスト実行（サマリー）"),
        ("python -m pytest test_*.py --cov=deliverManager --cov-report=term-missing", "テストカバレッジ計測（要pytest-cov）"),
        ("python deliverManager.py", "サンプル実行テスト"),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for command, description in tests:
        try:
            success = run_command(command, description)
            if success:
                passed_tests += 1
                print(f"✓ {description} - 成功")
            else:
                print(f"✗ {description} - 失敗")
        except Exception as e:
            print(f"✗ {description} - エラー: {e}")
    
    print(f"\n{'='*60}")
    print(f"テスト結果サマリー: {passed_tests}/{total_tests} 成功")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 全てのテストが成功しました！")
        return 0
    else:
        print("⚠️  一部のテストが失敗しました。")
        return 1


if __name__ == "__main__":
    sys.exit(main())