from collections import Counter
from statistics import mean


def validate_records(data):
    schema = {row['name']: row for row in data['schema']}
    reasons = {(row['student'], row['field']): row['reason'] for row in data['missing_reasons']}
    identities = set()
    for row in data['records']:
        if row['student'] in identities:
            raise ValueError('重复学生')
        identities.add(row['student'])
        for name, definition in schema.items():
            value = row.get(name)
            if value is None:
                if (row['student'], name) not in reasons:
                    raise ValueError('缺失值没有原因：' + name)
                continue
            if definition['type'] == 'number':
                if not isinstance(value, (int, float)) or not definition['min'] <= value <= definition['max']:
                    raise ValueError('数值越界：' + name)
            elif value not in definition['categories']:
                raise ValueError('未知类别：' + name)
        if all(row.get(name) is not None for name in ('part_a', 'part_b', 'score')):
            if abs(row['part_a'] + row['part_b'] - row['score']) > 1e-8:
                raise ValueError('总分与分项不符')
    return schema


def baseline(data):
    schema = validate_records(data)
    return {'records': len(data['records']),
            'missing': {name: sum(row.get(name) is None for row in data['records']) for name in schema},
            'reasons': dict(Counter(row['reason'] for row in data['missing_reasons']))}


def act(data, request):
    schema = validate_records(data)
    if request.get('operation') != 'complete_cases':
        raise ValueError('未知分析室操作')
    fields = request.get('fields', [])
    if not fields or any(field not in schema or schema[field]['type'] != 'number' for field in fields):
        raise ValueError('请选择数值字段')
    complete = [row for row in data['records'] if all(row.get(field) is not None for field in fields)]
    return {'fields': fields, 'retained': len(complete), 'excluded': len(data['records']) - len(complete),
            'means': {field: mean(row[field] for row in complete) if complete else None for field in fields},
            'notice': '完整记录描述，未假设缺失机制'}
