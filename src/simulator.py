# MAC 연산과 패턴 판정에 필요한 핵심 로직을 담는 모듈이다.

from typing import Dict, List, Union


Matrix = List[List[float]]
EvaluationValue = Union[float, str]
EvaluationResult = Dict[str, EvaluationValue]


def calculate_mac(pattern: Matrix, filter_matrix: Matrix) -> float:
    # 같은 위치의 값끼리 곱한 뒤 모두 더하는 핵심 연산 함수다.
    if len(pattern) != len(filter_matrix):
        raise ValueError("패턴과 필터의 행 개수가 다릅니다.")

    score = 0.0

    for row_idx in range(len(pattern)):
        if len(pattern[row_idx]) != len(filter_matrix[row_idx]):
            raise ValueError("패턴과 필터의 열 개수가 다릅니다.")

        # 같은 좌표의 값끼리 곱한 뒤 전체 점수에 누적한다.
        for col_idx in range(len(pattern[row_idx])):
            score += pattern[row_idx][col_idx] * filter_matrix[row_idx][col_idx]

    return score


def normalize_label(label: str) -> str:
    # expected 값이나 필터 이름이 달라도 내부에서는 Cross, X로 통일해 다룬다.
    normalized = label.strip().lower()

    if normalized in {"+", "cross"}:
        return "Cross"

    if normalized == "x":
        return "X"

    return label


def is_tie(score_a: float, score_b: float, epsilon: float = 1e-9) -> bool:
    # 부동소수점 오차를 고려해 epsilon 이내 차이는 같은 점수로 처리한다.
    return abs(score_a - score_b) < epsilon


def judge_scores(
    cross_score: float, x_score: float, epsilon: float = 1e-9
) -> str:
    # Cross 점수와 X 점수를 비교해 어느 필터와 더 유사한지 결정한다.
    # 두 점수 차이가 매우 작으면 판정을 보류한다.
    if is_tie(cross_score, x_score, epsilon):
        return "UNDECIDED"

    if cross_score > x_score:
        return "Cross"

    return "X"


def evaluate_pattern(
    pattern: Matrix,
    cross_filter: Matrix,
    x_filter: Matrix,
    epsilon: float = 1e-9,
) -> EvaluationResult:
    # 모드 1과 모드 2 모두에서 재사용할 수 있도록 평가 흐름을 하나로 묶는다.
    cross_score = calculate_mac(pattern, cross_filter)
    x_score = calculate_mac(pattern, x_filter)
    prediction = judge_scores(cross_score, x_score, epsilon)

    return {
        "cross_score": cross_score,
        "x_score": x_score,
        "prediction": prediction,
    }


def is_expected_match(prediction: str, expected_label: str) -> bool:
    # data.json 분석 모드에서 PASS/FAIL을 판단할 때 사용하는 비교 함수다.
    normalized_expected = normalize_label(expected_label)
    return prediction == normalized_expected
