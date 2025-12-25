import ast


def normalize_for_json(obj):
    if isinstance(obj, dict):
        return {k: normalize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_for_json(i) for i in obj]
    if isinstance(obj, str):
        try:
            return ast.literal_eval(obj)
        except Exception:
            return obj
    return obj