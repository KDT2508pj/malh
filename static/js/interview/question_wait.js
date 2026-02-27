/**
 * question_wait.js - 질문 생성 프로세스 시뮬레이션 (jQuery)
 */

$(document).ready(function() {
    let progress = 0;
    const $progressBar = $('#progressBar');
    const $percentageText = $('#percentageText');
    let retryCount = 0;

    /**
     * [Logic] 진행률 시뮬레이션 시작
     */
    function simulateGeneration() {
        const interval = setInterval(() => {
            // 랜덤하게 진행률 증가 (1~8%)
            const increment = Math.floor(Math.random() * 8) + 1;
            progress += increment;

            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                updateUI(progress);
                
                // 생성 완료 후 0.5초 뒤 이동
                setTimeout(() => {
                    location.href = '/interviews/1';
                }, 500); 
            } else {
                updateUI(progress);
            }
        }, 200); // 0.2초마다 상태 업데이트
    }

    /**
     * [UI Update] 진행률 표시 업데이트
     */
    function updateUI(value) {
        $progressBar.css('width', value + '%');
        $percentageText.text(value + '%');
    }

    /**
     * [Error Handling] 에러 발생 시나리오 처리
     */
    function handleError() {
        if (retryCount < 1) {
            console.log("Error detected. Retrying...");
            retryCount++;
            progress = 0;
            simulateGeneration();
        } else {
            location.href = '/';
        }
    }

    // 시뮬레이션 실행
    simulateGeneration();
});