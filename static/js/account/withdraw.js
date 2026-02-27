/**
 * withdraw.js - 회원 탈퇴 동의 및 처리 (jQuery)
 */

$(document).ready(function() {
    const $agreeCheck = $('#agreeCheck');
    const $withdrawBtn = $('#withdrawBtn');

    /**
     * [Logic 1] 체크박스 상태에 따라 버튼 활성화/비활성화
     */
    function toggleButton() {
        if ($agreeCheck.prop('checked')) {
            $withdrawBtn.addClass('active');
            $withdrawBtn.prop('disabled', false);
        } else {
            $withdrawBtn.removeClass('active');
            $withdrawBtn.prop('disabled', true);
        }
    }

    /**
     * [Logic 2] 탈퇴 처리 실행
     */
    function handleWithdraw() {
        if (!$agreeCheck.prop('checked')) {
            alert("탈퇴 유의사항에 동의해 주세요.");
            return;
        }

        // 최종 확인 컨펌창
        if (confirm("정말로 탈퇴하시겠습니까? 이 동작은 취소할 수 없습니다.")) {
            // 실제 구현 시: API를 통한 회원 정보 삭제 요청 로직 위치
            alert("회원 탈퇴 되었습니다.");
            
            // 메인 페이지로 이동
            location.href = "/";
        }
    }

    // 이벤트 리스너 등록
    $agreeCheck.on('change', toggleButton);
    $withdrawBtn.on('click', handleWithdraw);

    // 초기 버튼 상태 설정 (비활성화)
    $withdrawBtn.prop('disabled', true);
});