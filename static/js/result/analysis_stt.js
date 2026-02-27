/**
 * analysis_stt.js - 정밀 분석 결과 페이지 동작 로직 (jQuery version)
 */

$(function() {
    console.log("정밀 분석 결과(STT) 페이지가 로드되었습니다.");

    /**
     * [예시] 도움말 아이콘 툴팁 기능 확장 가능
     */
    $('.help-icon').on('mouseenter', function() {
        // 커스텀 툴팁 로직 작성 가능
    });
});

/**
 * 페이지 최상단으로 부드럽게 스크롤
 */
function scrollToTop() {
    $('html, body').animate({
        scrollTop: 0
    }, 'smooth');
}