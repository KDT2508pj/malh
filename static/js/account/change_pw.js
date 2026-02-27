/**
 * change_pw.js - 비밀번호 변경 동작 및 유효성 검사 (jQuery)
 */

$(document).ready(function() {
    const $newPwInput = $('#newPw');
    const $confirmPwInput = $('#confirmPw');
    const $newPwError = $('#newPwError');
    const $confirmError = $('#confirmError');

    // [Mock Data] 기존 비밀번호 (검증용 시뮬레이션)
    const MOCK_CURRENT_PW = "test1234!";

    // [Helper] 에러 메시지 표시
    function showError($input, $errorElement, message) {
        $input.addClass('input-error');
        $errorElement.text(message).show();
    }

    // [Helper] 에러 메시지 숨김
    function hideError($input, $errorElement) {
        $input.removeClass('input-error');
        $errorElement.hide();
    }

    // [Logic 1] 새 비밀번호 유효성 검사
    window.validateNewPw = function() {
        const val = $newPwInput.val();
        const regex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;

        if (!val) {
            showError($newPwInput, $newPwError, "새 비밀번호를 입력해 주세요.");
            return false;
        }
        if (!regex.test(val)) {
            showError($newPwInput, $newPwError, "8자 이상 영문, 숫자, 특수문자를 조합해 주세요.");
            return false;
        }
        if (val === MOCK_CURRENT_PW) {
            showError($newPwInput, $newPwError, "기존 비밀번호와 일치합니다. 다른 비밀번호를 사용해 주세요.");
            return false;
        }

        hideError($newPwInput, $newPwError);
        return true;
    };

    // [Logic 2] 비밀번호 확인 검사
    window.validateConfirmPw = function() {
        const val = $confirmPwInput.val();
        const original = $newPwInput.val();

        if (!val) {
            showError($confirmPwInput, $confirmError, "비밀번호 확인을 입력해 주세요.");
            return false;
        }
        if (val !== original) {
            showError($confirmPwInput, $confirmError, "비밀번호가 일치하지 않습니다.");
            return false;
        }

        hideError($confirmPwInput, $confirmError);
        return true;
    };

    // 실시간 검사 (blur 이벤트 바인딩)
    $newPwInput.on('blur', window.validateNewPw);
    $confirmPwInput.on('blur', window.validateConfirmPw);

    // [Logic 3] 변경하기 버튼 클릭 시 전체 검증
    window.submitChange = function() {
        const isNewValid = window.validateNewPw();
        const isConfirmValid = window.validateConfirmPw();

        if (isNewValid && isConfirmValid) {
            // 실제 API 통신 로직 대체
            alert("비밀번호가 성공적으로 변경되었습니다. 다시 로그인해 주세요.");
            location.href = "/auth/login";
        }
    };
});