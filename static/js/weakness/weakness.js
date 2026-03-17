/**
 * weakness.js - weakness question list interactions
 */

function getSessionIdFromPath() {
    const match = window.location.pathname.match(/\/interviews\/(\d+)/);
    return match ? Number(match[1]) : 0;
}

function goToWeaknessDetail(id, isRecorded = false) {
    const sessionId = getSessionIdFromPath();
    if (!sessionId || !id) {
        return;
    }
    if (isRecorded) {
        alert("이미 녹음이 완료된 질문입니다. 재녹음은 지원하지 않습니다.");
        return;
    }
    location.href = `/interviews/${sessionId}/weakness/${id}`;
}

function completeReinforcement() {
    const sessionId = getSessionIdFromPath();
    if (!sessionId) {
        return;
    }

    location.href = `/interviews/${sessionId}/weakness/report-loading`;
}
