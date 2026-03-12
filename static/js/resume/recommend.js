let loadingTimer = null;
let loadingProgress = 0;
let loadingFinished = false;

function wait(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function nextFrame() {
    return new Promise((resolve) => window.requestAnimationFrame(() => resolve()));
}

function updateLoadingUI(value, message) {
    const progressBar = document.getElementById("loadingProgressBar");
    const percent = document.getElementById("loadingPercent");
    const count = document.getElementById("loadingCount");
    const loadingMessage = document.getElementById("loadingMessage");

    if (progressBar) {
        progressBar.style.width = `${value}%`;
    }
    if (percent) {
        percent.textContent = `${Math.floor(value)}%`;
    }
    if (count) {
        count.textContent = value >= 100 ? "완료" : "분석 중";
    }
    if (loadingMessage) {
        loadingMessage.textContent = message;
    }
}

function startFakeLoading() {
    loadingFinished = false;
    loadingProgress = 0;
    updateLoadingUI(0, "데이터 정합성 검증 및 분석을 진행하고 있습니다.");

    loadingTimer = window.setInterval(() => {
        if (loadingFinished || loadingProgress >= 88) {
            return;
        }

        const increment = loadingProgress < 30
            ? 3
            : (loadingProgress < 65 ? 4 : 2);

        loadingProgress = Math.min(88, loadingProgress + increment);

        let message = "데이터 정합성 검증 및 분석을 진행하고 있습니다.";
        if (loadingProgress >= 30 && loadingProgress < 65) {
            message = "회사 정보와 기술 스택을 비교 분석하고 있습니다.";
        } else if (loadingProgress >= 65) {
            message = "분석 결과를 정리하고 있습니다.";
        }

        updateLoadingUI(loadingProgress, message);
    }, 120);
}

function stopFakeLoading(success) {
    loadingFinished = true;
    if (loadingTimer) {
        window.clearInterval(loadingTimer);
        loadingTimer = null;
    }

    if (success) {
        updateLoadingUI(loadingProgress, "분석 마무리 중입니다.");
    } else {
        updateLoadingUI(0, "분석 준비 중입니다.");
    }
}

async function animateLoadingToComplete() {
    if (loadingProgress < 15) {
        loadingProgress = 15;
        updateLoadingUI(loadingProgress, "데이터 정합성 검증 및 분석을 진행하고 있습니다.");
        await wait(180);
    }

    while (loadingProgress < 100) {
        const remaining = 100 - loadingProgress;
        const increment = remaining > 30 ? 4 : (remaining > 10 ? 3 : 1);
        loadingProgress = Math.min(100, loadingProgress + increment);
        updateLoadingUI(
            loadingProgress,
            loadingProgress >= 100 ? "분석이 완료되었습니다." : "분석 마무리 중입니다.",
        );
        await wait(45);
    }

    await wait(220);
}

function renderFeedbackResult(data) {
    const strengthsContent = document.getElementById("strengthsContent");
    const improvementsContent = document.getElementById("improvementsContent");
    const compatibilityWarning = document.getElementById("compatibilityWarning");
    const warningText = document.getElementById("warningText");

    strengthsContent.innerHTML = "";
    improvementsContent.innerHTML = "";

    if (compatibilityWarning) {
        compatibilityWarning.style.display = "none";
        compatibilityWarning.style.backgroundColor = "#fff3cd";
        compatibilityWarning.style.color = "#856404";
    }

    if (data.step1_ok === false) {
        if (compatibilityWarning) {
            compatibilityWarning.style.display = "block";
            warningText.innerText = "[직무 부적합] " + (data.mismatch_reason || "이력서가 회사의 직무 방향성과 일치하지 않습니다.");
        }
        strengthsContent.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">직무 전문 분야가 달라 분석을 진행할 수 없습니다.</p>';
        return;
    }

    if (data.step2_ok === false) {
        if (compatibilityWarning) {
            compatibilityWarning.style.display = "block";
            compatibilityWarning.style.backgroundColor = "#f8d7da";
            compatibilityWarning.style.color = "#721c24";
            warningText.innerText = "[기술 스택 오류] " + (data.mismatch_reason || "유효한 기술 키워드가 없습니다.");
        }
        strengthsContent.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">입력한 기술 스택이 해당 직무와 관련이 없습니다.</p>';
        return;
    }

    if (data.strengths && data.strengths.length > 0) {
        data.strengths.forEach((item) => {
            strengthsContent.innerHTML += `
                <div class="result-item" style="margin-top: 10px; border-bottom: 1px dashed #eee; padding-bottom: 10px;">
                    <p style="font-weight: bold; color: #2c3e50;">• ${item.title}</p>
                    <p style="font-size: 0.9em; color: #666; margin-left: 10px;">${item.description}</p>
                </div>`;
        });
    }

    if (data.improvements && data.improvements.length > 0) {
        data.improvements.forEach((item) => {
            improvementsContent.innerHTML += `
                <div class="result-item" style="margin-top: 10px; border-bottom: 1px dashed #eee; padding-bottom: 10px;">
                    <p style="font-weight: bold; color: #e67e22;">• ${item.title}</p>
                    <p style="font-size: 0.9em; color: #666; margin-left: 10px;">${item.description}</p>
                </div>`;
        });
    }
}

async function startAnalysis() {
    const resumeSelect = document.getElementById("resumeSelect");
    const selectedResumeId = resumeSelect.value;
    const companyUrl = document.getElementById("companyUrl").value;
    const companyStack = document.getElementById("companyStack").value;

    if (!selectedResumeId || !companyUrl.trim() || !companyStack.trim()) {
        alert("모든 정보를 입력해 주세요.");
        return;
    }

    document.getElementById("inputForm").style.display = "none";
    document.getElementById("loadingArea").style.display = "flex";
    document.getElementById("resultArea").style.display = "none";

    startFakeLoading();

    await nextFrame();
    await nextFrame();

    try {
        const response = await fetch("/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume_id: parseInt(selectedResumeId, 10),
                company_url: companyUrl,
                companyStack: companyStack,
            }),
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.detail || "분석 요청에 실패했습니다.");
        }

        stopFakeLoading(true);
        await animateLoadingToComplete();
        renderFeedbackResult(data);
        document.getElementById("loadingArea").style.display = "none";
        document.getElementById("resultArea").style.display = "block";
    } catch (error) {
        stopFakeLoading(false);
        alert("분석 중 오류 발생: " + (error.message || "알 수 없는 오류"));
        document.getElementById("loadingArea").style.display = "none";
        document.getElementById("inputForm").style.display = "block";
    }
}
