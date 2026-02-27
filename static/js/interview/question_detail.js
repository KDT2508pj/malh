/**
 * question_detail.js - 질문 상세 페이지 녹음 로직 (jQuery version)
 */

let timerInterval;
let seconds = 0;

/**
 * [Logic 1] 녹음 시작 프로세스
 */
function startRecordingFlow() {
    // 마이크 권한 확인 시뮬레이션
    if (confirm("마이크 사용 권한을 허용하시겠습니까?")) {
        // 1. 대기 화면 숨김
        $('#mode-standby').removeClass('active');
        
        // 2. 녹음 화면 표시
        $('#mode-recording').addClass('active');

        // 3. 타이머 시작
        startTimer();
    } else {
        alert("마이크 권한이 필요합니다.");
    }
}

/**
 * [Logic 2] 타이머 기능
 */
function startTimer() {
    const $timerElement = $('#timer');
    seconds = 0; // 초기화
    $timerElement.text("00:00");
    
    timerInterval = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        const timeString = 
            `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        $timerElement.text(timeString);
    }, 1000);
}

/**
 * [Logic 3] 녹음 완료 및 페이지 이동
 */
function finishRecording() {
    clearInterval(timerInterval); // 타이머 정지
    
    // 저장 알림
    alert("답변이 저장되었습니다. 질문 목록으로 이동합니다.");
    
    // 질문 목록 페이지로 이동
    $(location).attr('href', '/interviews/1');
}

$(function() {
    console.log("질문 상세 녹음 페이지가 로드되었습니다.");
});