/**
 * login.js - 로그인 페이지 인터랙션 및 유효성 검사 (jQuery)
 */

// 포커스 벗어날 때 빈 값 체크 로직
function validateInput(input) {
    const $input = $(input);
    const $errorMsg = $input.next('.error-message'); // 바로 다음 요소인 p.error-message 선택
    
    if ($input.val().trim() === "") {
        $input.css("border-color", "var(--error-red)");
        $errorMsg.addClass("show");
    } else {
        $input.css("border-color", "var(--border-color)");
        $errorMsg.removeClass("show");
    }
}

// 로그인 처리 로직
function handleLogin(event) {
    event.preventDefault(); // 폼 전송 막기

    const $userId = $('#userId');
    const $userPw = $('#userPw');

    // 강제로 유효성 검사 트리거 (버튼 클릭 시에도 검사) 
    validateInput($userId[0]);
    validateInput($userPw[0]);

    // 둘 중 하나라도 비어있으면 리턴 
    if ($userId.val().trim() === "" || $userPw.val().trim() === "") {
        return;
    }

    // 아이디/비밀번호 불일치 시나리오 (테스트용 모의 로직) 
    if ($userId.val() !== "test" || $userPw.val() !== "1234") {
        alert("아이디 또는 비밀번호가 일치하지 않습니다.");
        return;
    }

    // 로그인 성공 시
    alert("로그인에 성공하였습니다.");
    location.href = "/"; // 메인 페이지로 이동
}