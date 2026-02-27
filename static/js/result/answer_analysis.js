/**
 * answer_analysis.js - 답변 분석 단계별 시뮬레이션 로직 (jQuery version)
 */

$(function() {
    let progress = 0;
    const $progressBar = $('#progressBar');
    const $percentageText = $('#percentageText');
    const $statusTitle = $('#statusTitle');
    const $statusDesc = $('#statusDesc');

    // 단계별 텍스트 및 정보 데이터
    const stages = [
        {
            title: 'AI가 음성을 분석하고 있습니다...',
            desc: '음성파일을 분석하여 유창성, 명료성 등을 평가하고 있어요.'
        },
        {
            title: 'AI가 텍스트를 추출하고 있습니다...',
            desc: '음성파일을 분석하여 텍스트를 만들고 있어요.'
        },
        {
            title: 'AI가 텍스트를 분석하고 있습니다...',
            desc: '텍스트파일을 분석하여 논리성, 적합성 등을 평가하고 있어요.'
        }
    ];

    /**
     * 현재 분석 단계에 따른 UI 업데이트
     * @param {number} stageIndex - 0:음성, 1:STT, 2:텍스트
     */
    function updateStageUI(stageIndex) {
        // 1. 아이콘 전환
        $('.stage-icon').each(function(idx) {
            $(this).toggleClass('active', idx === stageIndex);
        });

        // 2. 텍스트 정보 전환
        $statusTitle.text(stages[stageIndex].title);
        $statusDesc.text(stages[stageIndex].desc);

        // 3. 단계 표시 점(Dot) 전환
        $('.step-dot').each(function(idx) {
            $(this).toggleClass('active', idx === stageIndex);
        });
    }

    /**
     * 분석 시뮬레이션 시작
     */
    function startSimulation() {
        const interval = setInterval(() => {
            // 랜덤한 수치로 진행률 증가
            progress += Math.random() * 1.5; 
            if (progress > 100) progress = 100;

            // 프로그레스 바 및 텍스트 업데이트
            $progressBar.css('width', progress + '%');
            $percentageText.text(Math.floor(progress) + '%');

            // 구간별 상태 체크 (33%, 70% 기준)
            if (progress < 33) {
                updateStageUI(0);
            } else if (progress < 70) {
                updateStageUI(1);
            } else {
                updateStageUI(2);
            }

            // 완료 시 결과 페이지로 이동
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    $(location).attr('href', '/interviews/1/results');
                }, 800);
            }
        }, 50);
    }

    // 시뮬레이션 실행
    startSimulation();
});