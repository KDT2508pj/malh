/**
 * agree.js - 약관 동의 페이지 동작 로직 (jQuery)
 */

$(document).ready(function() {
    const $checkAllBox = $('#checkAll');
    const $allCheckboxes = $('.terms-list input[type="checkbox"]');
    const $requiredTerms = $('.terms-list input.required');
    const $nextBtn = $('#nextBtn');
    const $modal = $('#termsModal');
    const $modalTitle = $('#modalTitle');
    const $modalBody = $('#modalBody');

    // 가상의 약관 데이터
    const termsData = {
        service: "말해뭐해 서비스 이용약관...\n(상세 내용 생략)",
        privacy: "개인정보 수집 및 이용 동의...\n(상세 내용 생략)",
        marketing: "마케팅 정보 수신 동의...\n(상세 내용 생략)"
    };

    // [전체 동의] 체크박스 이벤트
    $checkAllBox.on('change', function() {
        $allCheckboxes.prop('checked', $(this).prop('checked'));
        updateButtonState();
    });

    // [개별 체크박스] 이벤트
    $allCheckboxes.on('change', function() {
        const allChecked = $allCheckboxes.length === $allCheckboxes.filter(':checked').length;
        $checkAllBox.prop('checked', allChecked);
        updateButtonState();
    });

    // 필수 약관 동의 여부에 따른 버튼 활성화
    function updateButtonState() {
        const requiredAllChecked = $requiredTerms.length === $requiredTerms.filter(':checked').length;
        if (requiredAllChecked) {
            $nextBtn.prop('disabled', false).addClass('active');
        } else {
            $nextBtn.prop('disabled', true).removeClass('active');
        }
    }

    // 모달 열기
    window.openModal = function(type) {
        $modal.css('display', 'flex');
        if (type === 'service') {
            $modalTitle.text("서비스 이용약관");
            $modalBody.text(termsData.service);
        } else if (type === 'privacy') {
            $modalTitle.text("개인정보 수집 및 이용 동의");
            $modalBody.text(termsData.privacy);
        } else if (type === 'marketing') {
            $modalTitle.text("마케팅 정보 수신 동의");
            $modalBody.text(termsData.marketing);
        }
    };

    // 모달 닫기
    window.closeModal = function() {
        $modal.hide();
    };

    // 모달 외부 클릭 시 닫기
    $(window).on('click', function(event) {
        if ($(event.target).is($modal)) {
            closeModal();
        }
    });

    // 다음 단계로 이동
    window.goToNextStep = function() {
        if (!$('#nextBtn').prop('disabled')) {
            location.href = '/auth/signup';
        } else {
            alert("필수 약관에 동의해 주세요.");
        }
    };
});