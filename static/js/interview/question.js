/**
 * question.js - interview question list interactions
 */

const interviewContext = window.INTERVIEW_CONTEXT || {};
const sessionId = Number(interviewContext.sessionId || 0);

function goToDetail(selId) {
    if (!sessionId || !selId) {
        return;
    }
    location.href = `/interviews/${sessionId}/questions/${selId}`;
}

function submitAnswers() {
    if (!sessionId) {
        return;
    }

    const $btn = $(".submit-btn");
    $btn.prop("disabled", true).text("분석 중...");

    fetch(`/api/interviews/${sessionId}/submit-analysis/start`, {
        method: "POST",
    })
        .then(async (response) => {
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(data.detail || "제출 분석에 실패했습니다.");
            }
            location.href = `/interviews/${sessionId}/submit-loading`;
        })
        .catch((error) => {
            alert(error.message || "제출 분석에 실패했습니다.");
        })
        .finally(() => {
            $btn.prop("disabled", false).text("제출하기");
        });
}

$(function () {
    console.log("question list loaded");
});
