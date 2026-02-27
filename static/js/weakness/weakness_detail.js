/**
 * weakness_detail.js - 약점 보강 녹음 페이지 동작 로직 (jQuery version)
 */

let timerInterval;
let seconds = 0;

/**
 * [Logic 1] 녹음 시작 프로세스 (대기 -> 녹음 중)
 */
function startRecordingFlow() {
    // 마이크 권한 확인 (시뮬레이션)
    if (confirm("마이크 사용 권한을 허용하시겠습니까?")) {
        // 1. 대기 화면 숨김 & 녹음 화면 표시
        $('#mode-standby').removeClass('active');
        $('#mode-recording').addClass('active');

        // 2. 타이머 시작
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
 * [Logic 3] 녹음 완료 및 저장
 */
function finishRecording() {
    clearInterval(timerInterval); // 타이머 정지
    
    // 저장 알림
    alert("보강 답변이 저장되었습니다.");
    
    // 약점 보강 질문 목록으로 이동
    $(location).attr('href', '/interviews/1/weakness');
}

$(function() {
    console.log("약점 보강 녹음 상세 페이지가 로드되었습니다.");
});