/**
 * resume_wait.js
 * 이력서 분석 + 질문 생성 대기 페이지 로직
 *
 * 동작:
 * 1. 페이지 로드
 * 2. /resumes/{resume_id}/analyze POST 호출
 * 3. 진행률은 95%까지만 시뮬레이션
 * 4. 서버 응답 성공 시 100%로 채우고 /resumes 로 이동
 */

let progress = 0;
let progressInterval = null;
let isCompleted = false;

const progressBar = document.getElementById('progressBar');
const percentageText = document.getElementById('percentageText');

function updateUI(value) {
    if (progressBar) {
        progressBar.style.width = value + '%';
    }
    if (percentageText) {
        percentageText.textContent = value + '%';
    }
}

function startProgressSimulation() {
    progressInterval = setInterval(() => {
        if (isCompleted) {
            clearInterval(progressInterval);
            return;
        }

        // 실제 완료 전에는 95%까지만 천천히 증가
        if (progress < 95) {
            const increment = Math.floor(Math.random() * 4) + 1; // 1~4
            progress += increment;

            if (progress > 95) {
                progress = 95;
            }

            updateUI(progress);
        }
    }, 200);
}

async function analyzeResume(resumeId, model) {
    const formData = new FormData();
    formData.append('model', model);

    const response = await fetch(`/resumes/${resumeId}/analyze`, {
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
                : '이력서 분석 및 질문 생성 중 오류가 발생했습니다.';
        throw new Error(message);
    }

    return result;
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
        startProgressSimulation();

        await analyzeResume(resumeId, model);

        isCompleted = true;
        clearInterval(progressInterval);

        progress = 100;
        updateUI(progress);

        setTimeout(() => {
            alert('이력서 분석과 질문 생성이 완료되었습니다.');
            location.href = '/resumes';
        }, 500);
    } catch (error) {
        isCompleted = true;
        clearInterval(progressInterval);

        alert(error.message || '분석 처리 중 오류가 발생했습니다.');
        location.href = '/resumes';
    }
}

window.onload = () => {
    updateUI(0);
    runAnalysis();
};