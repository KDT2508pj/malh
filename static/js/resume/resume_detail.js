/**
 * resume_detail.js - 이력서 상세 페이지 동작 로직 (jQuery)
 */

function switchTab(tabName, element) {
    $('.tab-content').removeClass('active');

    const $selectedContent = $('#tab-' + tabName);
    if ($selectedContent.length) {
        $selectedContent.addClass('active');
    }

    $('.tab-item').removeClass('active');

    if (element) {
        $(element).addClass('active');
    }
}

function startPractice(resumeId) {
    const $btn = $('#startPracticeBtn');
    const originalText = $btn.text();

    $btn.prop('disabled', true).text('문제 준비 중...');

    $.ajax({
        url: `/resumes/${resumeId}/start-practice`,
        method: 'POST',
        contentType: 'application/json',
        success: function (response) {
            if (response && response.session_id) {
                location.href = `/interviews/${response.session_id}/wait`;
                return;
            }

            $btn.prop('disabled', false).text(originalText);
            alert('세션 정보가 올바르지 않습니다.');
        },
        error: function (xhr) {
            $btn.prop('disabled', false).text(originalText);

            let message = '연습 시작 중 오류가 발생했습니다.';
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                message = xhr.responseJSON.detail;
            }

            alert(message);
        }
    });
}

$(document).ready(function () {
    $('#startPracticeBtn').on('click', function () {
        const resumeId = $(this).data('resume-id');
        startPractice(resumeId);
    });
});