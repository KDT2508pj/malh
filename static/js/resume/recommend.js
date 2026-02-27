/**
 * recommend.js - 이력서 피드백 분석 시뮬레이션 (jQuery)
 */

function startAnalysis() {
    const $resumeSelect = $('#resumeSelect');
    const $companyUrl = $('#companyUrl');
    const $inputForm = $('#inputForm');
    const $loadingArea = $('#loadingArea');
    const $resultArea = $('#resultArea');

    // [Logic 1] 유효성 검사
    if (!$resumeSelect.val()) {
        if (confirm("분석할 이력서가 선택되지 않았습니다. 이력서 관리 페이지로 이동하시겠습니까?")) {
            location.href = 'resume.html';
        }
        return;
    }

    if (!$companyUrl.val().trim()) {
        alert("채용 공고 URL 또는 정보를 입력해 주세요.");
        $companyUrl.focus();
        return;
    }

    // [Logic 2] UI 전환: 입력 -> 로딩
    $inputForm.hide();
    $loadingArea.show();

    // [Logic 3] 시뮬레이션 (3초 후 결과 표시)
    setTimeout(() => {
        // 실제 구현 시: 서버 API 호출 및 크롤링 데이터 수신
        $loadingArea.hide();
        $resultArea.show();
    }, 3000);
}