/**
 * analysis_text.js - 답변 텍스트 분석 결과 페이지 로직 (jQuery version)
 */

$(function() {
    console.log("텍스트 분석 결과 페이지가 로드되었습니다.");
});

/**
 * 탭 전환 기능
 * @param {string} tabName - 표시할 탭의 ID
 * @param {HTMLElement} element - 클릭된 탭 요소
 */
function switchTab(tabName, element) {
    // 1. 모든 탭 컨텐츠 숨김
    $('.tab-content').removeClass('active');

    // 2. 선택한 탭 컨텐츠 표시
    $('#tab-' + tabName).addClass('active');

    // 3. 모든 탭 버튼 비활성화
    $('.tab-item').removeClass('active');

    // 4. 클릭한 탭 버튼 활성화
    if (element) {
        $(element).addClass('active');
    }
}

/**
 * 약점 보강하기 페이지로 이동
 */
function goToWeakness() {
    $(location).attr('href', 'weakness_wait.html');
}