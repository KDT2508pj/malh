/**
 * answer_analysis.js - waits while backend STT runs, then moves to results page
 */

$(function () {
    let progress = 0;
    let sttStarted = false;
    let sttPromise = null;

    const $progressBar = $("#progressBar");
    const $percentageText = $("#percentageText");
    const $statusTitle = $("#statusTitle");
    const $statusDesc = $("#statusDesc");

    const stages = [
        {
            title: "AI가 음성을 분석하고 있습니다...",
            desc: "음성 파일에서 발화 특성을 추출하고 있습니다.",
        },
        {
            title: "AI가 텍스트를 추출하고 있습니다...",
            desc: "업로드된 음성을 STT로 변환하고 있습니다.",
        },
        {
            title: "AI가 텍스트를 분석하고 있습니다...",
            desc: "전사된 텍스트를 기반으로 후속 분석을 준비하고 있습니다.",
        },
    ];

    function getPathContext() {
        const match = window.location.pathname.match(/\/interviews\/(\d+)\/results\/(\d+)\/analysis/);
        if (!match) return null;
        return {
            sessionId: Number(match[1]),
            selId: Number(match[2]),
        };
    }

    async function triggerStt() {
        const context = getPathContext();
        if (!context) {
            throw new Error("Invalid analysis page path.");
        }

        const response = await fetch(
            `/api/interviews/${context.sessionId}/questions/${context.selId}/stt`,
            { method: "POST" },
        );
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || "STT 요청에 실패했습니다.");
        }
        return response.json();
    }

    function updateStageUI(stageIndex) {
        $(".stage-icon").each(function (idx) {
            $(this).toggleClass("active", idx === stageIndex);
        });

        $statusTitle.text(stages[stageIndex].title);
        $statusDesc.text(stages[stageIndex].desc);

        $(".step-dot").each(function (idx) {
            $(this).toggleClass("active", idx === stageIndex);
        });
    }

    function redirectToResults() {
        const context = getPathContext();
        if (!context) {
            window.location.href = "/";
            return;
        }
        window.location.href = `/interviews/${context.sessionId}/results/${context.selId}/stt`;
    }

    async function finishFlow() {
        try {
            if (sttPromise) {
                await sttPromise;
            }
            redirectToResults();
        } catch (error) {
            alert(error.message || "STT 처리에 실패했습니다.");
        }
    }

    function startSimulation() {
        const interval = setInterval(() => {
            progress += Math.random() * 1.5;
            if (progress > 100) progress = 100;

            $progressBar.css("width", `${progress}%`);
            $percentageText.text(`${Math.floor(progress)}%`);

            if (progress < 33) {
                updateStageUI(0);
            } else if (progress < 70) {
                updateStageUI(1);
            } else {
                updateStageUI(2);
            }

            if (!sttStarted && progress >= 35) {
                sttStarted = true;
                sttPromise = triggerStt();
            }

            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    void finishFlow();
                }, 500);
            }
        }, 50);
    }

    startSimulation();
});
