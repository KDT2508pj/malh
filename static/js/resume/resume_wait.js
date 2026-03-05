const progressBar = document.getElementById('progressBar');
const percentageText = document.getElementById('percentageText');
const statusText = document.getElementById('statusText');

let pollTimer = null;
let isPolling = false;

const STATUS_LABEL_MAP = {
    UPLOADED: '업로드가 완료되었습니다.',
    CLASSIFYING: '이력서 직무 분류 중입니다...',
    STRUCTURING: '이력서 구조화 분석 중입니다...',
    KEYWORDS_EXTRACTING: '핵심 키워드 추출 중입니다...',
    KEYWORDS_DONE: '이력서 분석이 완료되었습니다. 질문 생성 준비 중입니다...',
    QUESTION_GENERATING: '면접 질문 생성 중입니다...',
    DONE: '모든 작업이 완료되었습니다.',
    FAILED: '처리 중 오류가 발생했습니다.',
};

function updateUI(progress, status) {
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }

    if (percentageText) {
        percentageText.textContent = `${progress}%`;
    }

    if (statusText) {
        statusText.textContent = STATUS_LABEL_MAP[status] || '처리 중입니다...';
    }
}

async function startAnalysis(resumeId, model) {
    const formData = new FormData();
    formData.append('model', model);

    const response = await fetch(`/resumes/${resumeId}/analyze/start`, {
        method: 'POST',
        body: formData,
    });

    let result = null;
    try {
        result = await response.json();
    } catch (e) {
        result = null;
    }

    if (!response.ok) {
        const message =
            result && result.detail
                ? result.detail
                : '분석 시작 중 오류가 발생했습니다.';
        throw new Error(message);
    }

    return result;
}

async function fetchStatus(resumeId) {
    const response = await fetch(`/resumes/${resumeId}/status`);

    let result = null;
    try {
        result = await response.json();
    } catch (e) {
        result = null;
    }

    if (!response.ok) {
        const message =
            result && result.detail
                ? result.detail
                : '상태 조회 중 오류가 발생했습니다.';
        throw new Error(message);
    }

    return result;
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

async function pollOnce(resumeId) {
    if (isPolling) return;
    isPolling = true;

    try {
        const statusResult = await fetchStatus(resumeId);
        const progress = Number(statusResult.progress || 0);
        const status = statusResult.status || 'UPLOADED';

        updateUI(progress, status);

        if (status === 'DONE') {
            stopPolling();
            setTimeout(() => {
                location.href = statusResult.detail_url || `/resumes/${resumeId}`;
            }, 400);
            return;
        }

        if (status === 'FAILED') {
            stopPolling();
            alert(statusResult.error_message || '이력서 분석 중 오류가 발생했습니다.');
            location.href = '/resumes';
            return;
        }
    } finally {
        isPolling = false;
    }
}

async function runAnalysis() {
    const root = document.getElementById('resumeWaitPage');
    if (!root) {
        alert('페이지 설정값을 찾을 수 없습니다.');
        location.href = '/resumes';
        return;
    }

    const resumeId = root.dataset.resumeId;
    const model = root.dataset.model || 'gpt-4o-mini';

    if (!resumeId) {
        alert('resume_id가 없습니다.');
        location.href = '/resumes';
        return;
    }

    try {
        updateUI(0, 'UPLOADED');

        await startAnalysis(resumeId, model);

        await pollOnce(resumeId);

        pollTimer = setInterval(() => {
            pollOnce(resumeId).catch((error) => {
                stopPolling();
                alert(error.message || '상태 확인 중 오류가 발생했습니다.');
                location.href = '/resumes';
            });
        }, 1200);
    } catch (error) {
        stopPolling();
        alert(error.message || '분석 처리 중 오류가 발생했습니다.');
        location.href = '/resumes';
    }
}

window.addEventListener('load', runAnalysis);