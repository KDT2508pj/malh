/**
 * weakness.js - weakness question list interactions
 */

function getSessionIdFromPath() {
    const match = window.location.pathname.match(/\/interviews\/(\d+)/);
    return match ? Number(match[1]) : 0;
}

function goToWeaknessDetail(id) {
    const sessionId = getSessionIdFromPath();
    if (!sessionId || !id) return;
    $(location).attr("href", `/interviews/${sessionId}/weakness/${id}`);
}

function completeReinforcement() {
    const sessionId = getSessionIdFromPath();
    if (!sessionId) return;

    if (confirm("보강 연습 결과를 분석해 개선 추적 리포트를 확인하시겠습니까?")) {
        $(location).attr("href", `/interviews/${sessionId}/weakness/report`);
    }
}

$(function () {
    console.log("weakness list loaded");
});
