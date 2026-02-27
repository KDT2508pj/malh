/**
 * sign_up.js - 회원가입 정보 입력 동작 로직 (jQuery)
 */

// 1. 비밀번호 유효성 검사
function validatePassword() {
    const pw = $('#userPw').val();
    const $helper = $('#pwHelper');
    const regex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;

    if (regex.test(pw)) {
        $helper.text("사용 가능한 비밀번호입니다.");
        $helper.attr("class", "helper-text success");
    } else {
        $helper.text("8자 이상 영문, 숫자, 특수문자를 조합해주세요.");
        $helper.attr("class", "helper-text error");
    }
}

// 2. 비밀번호 일치 확인
function comparePassword() {
    const pw = $('#userPw').val();
    const confirmPw = $('#userPwConfirm').val();
    const $helper = $('#pwConfirmHelper');

    if (confirmPw === "") {
        $helper.text("");
    } else if (pw === confirmPw) {
        $helper.text("비밀번호가 일치합니다.");
        $helper.attr("class", "helper-text success");
    } else {
        $helper.text("비밀번호가 일치하지 않습니다.");
        $helper.attr("class", "helper-text error");
    }
}

// 3. 중복 확인 (시뮬레이션)
function checkDuplicate(type) {
    const value = type === 'id' ? $('#userId').val() : $('#userEmail').val();
    
    if (!value) {
        alert("값을 입력해주세요.");
        return;
    }

    // 실제로는 서버 API 호출
    alert(`${value}은(는) 사용 가능한 ${type === 'id' ? '아이디' : '이메일'}입니다.`);
    
    if (type === 'id') {
        const $idHelper = $('#idHelper');
        $idHelper.text("확인 완료");
        $idHelper.attr("class", "helper-text success");
    }
}

// 4. 가입 처리
function handleSignup(event) {
    event.preventDefault();
    
    // 유효성 체크 로직 추가 가능
    
    alert("회원가입이 완료되었습니다!");
    location.href = '/auth/login'; // 로그인 페이지로 이동
}