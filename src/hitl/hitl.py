"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 12: Confidence Router
  TODO 13: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 12: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type."""
        
        # 1. High_risk_actions always escalate regardless of confidence
        if action_type in HIGH_RISK_ACTIONS:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason=f"High-risk action: {action_type}",
                priority="high",
                requires_human=True,
            )
            
        # 2. Confidence thresholds
        if confidence >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                action="auto_send",
                confidence=confidence,
                reason="High confidence",
                priority="low",
                requires_human=False,
            )
        elif confidence >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                action="queue_review",
                confidence=confidence,
                reason="Medium confidence — needs review",
                priority="normal",
                requires_human=True,
            )
        else:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason="Low confidence — escalating",
                priority="high",
                requires_human=True,
            )


# ============================================================
# TODO 13: Design 3 HITL decision points
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "Kiểm Duyệt Giao Dịch Bất Thường (High-Risk Anomaly)",
        "trigger": "Phát sinh giao dịch chuyển khoản giá trị cực lớn hoặc chuyển ra khỏi khu vực địa lý thông thường (IP lạ).",
        "hitl_model": "human-in-the-loop",
        "context_needed": "User profile, lịch sử giao dịch gần nhất, thông tin vị trí IP hiện tại, nội dung phân tích rủi ro của AI Risk Scoring.",
        "example": "Người dùng đăng nhập từ IP Châu Âu lúc 2h sáng theo múi giờ sở tại và đòi chuyển 500 triệu. AI sẽ BLOCK lại (chặn Request gửi chuyển khoản lên bank_api), nhả về trạng thái Pending. Sau đó đợi hệ thống CSKH con người (Reviewer Level 2) gọi điện xác minh và trực tiếp check lại thông tin, nếu an toàn CSKH mới ấn vào nút [APPROVE] thì tiền mới rời đi.",
    },
    {
        "id": 2,
        "name": "Phê Duyệt Giải Ngân Khoản Vay Tín Chấp Dưới 20 Triệu",
        "trigger": "Người dùng yêu cầu vay tiền nhanh trên app và hệ thống tính điểm AI (Credit Scoring) của VinBank chấm khách hàng vượt ngưỡng điểm An toàn Tốt.",
        "hitl_model": "human-on-the-loop",
        "context_needed": "Điểm tín dụng CIC / Credit Score, hồ sơ thu nhập hàng tháng (sao kê đóng lương thu thập được) do AI tổng hợp tự động.",
        "example": "Do tỷ lệ trượt nợ ở khoảng vay 10 triệu cho người có CIC cao là cực hiếm, AI được VinBank cho quyền TỰ ĐỘNG CHẤP THUẬN và giải ngân ngay lập tức đổ tiền về ví khách hàng. TRONG LÚC ĐÓ MÀ SAU KHI LUỒNG ĐÃ ĐI, thông báo sẽ lưu về hàng đợi cho ban Giám sát tín dụng (Hotline Audit). Chuyên viên lôi ngẫu nhiên 5% hồ sơ ra chấm tay, nếu phát hiện lừa đảo thì đánh lùi huỷ quyền cho các lượt thuật toán AI tương lai.",
    },
    {
        "id": 3,
        "name": "Giải Quyết Khiếu Nại Hoàn Tiền Thẻ Quẹt (Chống Phẫn Nộ Mất Khách)",
        "trigger": "Phân tích Alert chỉ ra người dùng đang bực tức, đe doạ muốn kiện / đòi khoá thẻ do giao dịch máy ATM bị lỗi nuốt tiền (AI không chắc nguyên nhân từ người hay phía bank, confidence score < 0.7).",
        "hitl_model": "human-as-tiebreaker",
        "context_needed": "Transcript đoạn chat tranh chấp, cờ đánh dấu thái độ khách hàng phẫn nộ (Aggression Flag), lịch sử thẻ POS và Error Code nội bộ.",
        "example": "Khách hàng dọa sẽ báo công an gỡ sổ ngân hàng nếu không hoàn lại số tiền 5 triệu quẹt lỗi POS hôm qua. Bởi hành vi Hoàn Tiền là (HIGH-RISK), hơn nữa Cảm xúc khách lại Phẫn Nộ (LOW Confidence cho sự đồng cảm của máy móc). AI LẬP TỨC từ bỏ quyền chat và nhấc TICKET TIE-BREAKER gọi Trưởng Bộ Phận Chăm Sóc Khách Hàng. Chuyên viên con người nhảy vào cướp Frame tiếp tục đoạn chat xoa dịu và xử lý thủ công mã nạp tiền.",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    test_confidence_router()
    test_hitl_points()
