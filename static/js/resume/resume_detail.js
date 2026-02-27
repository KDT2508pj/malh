/**
 * resume_detail.js - 이력서 상세 페이지 동작 로직 (jQuery)
 */

// 연습 시작하기 버튼 로직
function startPractice() {
    location.href = 'question_wait.html';
}

/**
 * 탭 전환 로직
 * @param {string} tabName - 표시할 탭의 ID 부분
 * @param {HTMLElement} element - 클릭된 탭 요소
 */
function switchTab(tabName, element) {
    // 1. 모든 탭 컨텐츠 숨기기
    $('.tab-content').removeClass('active');

    // 2. 선택한 탭 컨텐츠 보이기
    const $selectedContent = $('#tab-' + tabName);
    if ($selectedContent.length) {
        $selectedContent.addClass('active');
    }

    // 3. 모든 탭 버튼 활성화 상태 제거
    $('.tab-item').removeClass('active');

    // 4. 클릭한 탭 버튼 활성화
    if (element) {
        $(element).addClass('active');
    }
}

$(document).ready(function() {
    console.log("이력서 상세 페이지가 로드되었습니다.");
});