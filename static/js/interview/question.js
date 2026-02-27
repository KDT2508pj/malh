/**
 * question.js - 예상 질문 리스트 페이지 동작 로직 (jQuery version)
 */

/**
 * [Logic 1] 질문 상세 페이지로 이동
 * @param {number} id - 선택된 질문의 고유 식별자
 */
function goToDetail(id) {
    // 실제 서버 환경에서는 라우팅 경로를 사용합니다.
    location.href = `/interviews/1/questions/${id}`;
}

/**
 * [Logic 2] 전체 답변 제출 처리
 */
function submitAnswers() {
    // 실제 서비스에서는 모든 질문의 'done' 상태 여부를 체크하는 유효성 검사가 필요합니다.
    
    // 제출 확인 알림
    alert("답변이 성공적으로 제출되었습니다. 분석 결과를 확인하세요.");
    
    // 답변 분석 리포트 페이지로 이동
    location.href = '/interviews/1/results';
}

$(function() {
    console.log("예상 질문 리스트가 로드되었습니다.");
});