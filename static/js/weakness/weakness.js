/**
 * weakness.js - 약점 보강 질문 리스트 페이지 로직 (jQuery version)
 */

$(function() {
    console.log("약점 보강 리스트 페이지가 로드되었습니다.");
});

/**
 * 약점 보강 상세 녹음 페이지로 이동
 * @param {number} id - 질문 ID
 */
function goToWeaknessDetail(id) {
    // 실제 구현 시 질문 ID를 쿼리 파라미터로 전달할 수 있습니다.
    $(location).attr('href', `/interviews/1/weakness/${id}`); 
}

/**
 * 모든 보강 연습 완료 후 최종 결과 확인
 */
function completeReinforcement() {
    if(confirm("모든 보강 연습을 마치고 최종 결과를 확인하시겠습니까?")) {
        // 통합 답변 분석 페이지로 이동
        $(location).attr('href', '/interviews/1/results'); 
    }
}