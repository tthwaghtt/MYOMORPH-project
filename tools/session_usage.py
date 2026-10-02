"""MYOMORPH 작업량 기록기: 세션별 토큰, 생각(thinking) 토큰, 작업 시간, 비용.

Usage:
  python3 tools/session_usage.py                 # 표 출력
  python3 tools/session_usage.py --append LABEL  # docs/usage-log.md 에 스냅샷 추가

원천은 Claude Code 세션 기록(~/.claude/projects/*/*.jsonl)의 마지막 `cost-state` 항목이다.
하네스가 직접 집계한 값이라 가장 정확하다. 컨테이너가 바뀌면 이전 기록 파일이 사라질 수
있으므로, 게이트마다 --append 로 스냅샷을 레포에 남기고 P7에서 합산한다.
"""
import glob, json, os, sys
from datetime import datetime, timezone

LOG = os.path.join(os.path.dirname(__file__), '..', 'docs', 'usage-log.md')


def last_cost_state(path):
    last = None
    for line in open(path, encoding='utf-8'):
        if '"cost-state"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get('type') == 'cost-state':
            last = d
    return last


def summarize(cs):
    models = cs.get('modelUsage', {})
    tot = lambda k: sum(m.get(k, 0) for m in models.values())
    return {
        'session': cs['sessionId'][:8],
        'start': datetime.fromtimestamp(cs['startTime'] / 1000, timezone.utc),
        'output': tot('outputTokens'),
        'thinking': tot('thinkingTokens'),
        'input': tot('inputTokens'),
        'cache_write': tot('cacheCreationInputTokens'),
        'cache_read': tot('cacheReadInputTokens'),
        'web_search': tot('webSearchRequests'),
        'model_s': cs.get('totalAPIDuration', 0) / 1000,
        'tool_s': cs.get('totalToolDuration', 0) / 1000,
        'session_s': cs.get('totalDuration', 0) / 1000,
        'cost': cs.get('totalCostUSD', 0.0),
        'lines_added': cs.get('totalLinesAdded', 0),
        'models': ', '.join(models),
    }


def row(s, label=''):
    h = lambda sec: f"{sec / 3600:.2f} h"
    return (f"| {label or s['session']} | {s['start']:%Y-%m-%d} | {s['output']:,} | {s['thinking']:,} | "
            f"{s['input'] + s['cache_write']:,} | {s['cache_read']:,} | {h(s['model_s'])} | {h(s['tool_s'])} | "
            f"{h(s['session_s'])} | ${s['cost']:.2f} |")


HEADER = ("| 기록 | 시작일 | 출력 토큰 | 생각 토큰 | 입력 토큰(신규+캐시쓰기) | 캐시 읽기 | 모델 생각·생성 시간 | 도구 실행 시간 | 세션 활성 시간 | 비용 |\n"
          "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

if __name__ == '__main__':
    stats = [summarize(cs) for p in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl'))
             if (cs := last_cost_state(p))]
    if '--append' in sys.argv:
        label = sys.argv[sys.argv.index('--append') + 1]
        with open(LOG, 'a', encoding='utf-8') as f:
            for s in stats:
                f.write(row(s, f"{label} ({s['session']})") + '\n')
    print(HEADER)
    for s in stats:
        print(row(s))
