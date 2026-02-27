/**
 * weakness_wait.js - 약점 보강 질문 생성 시뮬레이션 로직 (jQuery version)
 */

$(function() {
    let progress = 0;
    const $progressBar = $('#progressBar');
    const $percentageText = $('#percentageText');

    /**
     * 진행률 업데이트 및 페이지 이동 처리
     */
    function simulateGeneration() {
        const interval = setInterval(() => {
            // 랜덤하게 진행률 증가 (2~6%)
            const increment = Math.floor(Math.random() * 5) + 2;
            progress += increment;

            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                updateUI(progress);
                
                // 완료 후 0.5초 뒤 약점 보강 실전 페이지로 이동
                setTimeout(() => {
                    $(location).attr('href', 'weakness_practice.html'); 
                }, 500);
            } else {
                updateUI(progress);
            }
        }, 150); // 0.15초마다 상태 체크
    }

    /**
     * UI 요소(바 너비, 텍스트) 업데이트
     * @param {number} value - 현재 진행률
     */
    function updateUI(value) {
        $progressBar.css('width', value + '%');
        $percentageText.text(value + '%');
    }

    // 시뮬레이션 시작
    simulateGeneration();
});