/**
 * analysis_stt.js - speech score detail page interactions
 */

$(function () {
    const $btn = $("#generateFeedbackBtn");
    const $status = $("#feedbackStatus");
    const $reportBox = $("#llmReportBox");
    const $coachingBox = $("#llmCoachingBox");
    const $reportContent = $("#llmReportContent");
    const $coachingContent = $("#llmCoachingContent");

    async function generateFeedback() {
        const sessionId = Number($btn.data("session-id") || 0);
        const selId = Number($btn.data("sel-id") || 0);
        if (!sessionId || !selId) {
            alert("Invalid page context.");
            return;
        }

        $btn.prop("disabled", true).text("LLM 피드백 생성 중...");
        $status.text("발화 지표를 기반으로 분석 리포트와 코칭 피드백을 생성하고 있습니다.");

        const formData = new FormData();
        formData.append("force", "1");

        try {
            const response = await fetch(`/api/interviews/${sessionId}/questions/${selId}/speech-feedback`, {
                method: "POST",
                body: formData,
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(data.detail || "LLM feedback request failed.");
            }

            $reportContent.text(data.report_md || "");
            $coachingContent.text(data.coaching_md || "");
            $reportBox.removeClass("hidden");
            $coachingBox.removeClass("hidden");
            $status.text("LLM 피드백이 생성되었습니다.");
        } catch (error) {
            $status.text("");
            alert(error.message || "LLM feedback generation failed.");
        } finally {
            $btn.prop("disabled", false).text("LLM 피드백 다시 생성");
        }
    }

    if ($btn.length) {
        if ($reportContent.text().trim() || $coachingContent.text().trim()) {
            $btn.text("LLM 피드백 다시 생성");
        }
        $btn.on("click", () => {
            void generateFeedback();
        });
    }
});

function scrollToTop() {
    $("html, body").animate({ scrollTop: 0 }, 250);
}